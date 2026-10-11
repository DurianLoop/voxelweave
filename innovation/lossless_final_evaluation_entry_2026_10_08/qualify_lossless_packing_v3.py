"""Qualify only lossless storage compatibility and unchanged science code, in memory."""
import sys,json,ast,copy,io,zipfile,time,traceback
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OUT=HERE/'compression_qualification_v3'
sys.path.insert(0,str(ROOT/'seranet_identity_prior_art_2026_10_08'))
import query_seranet_stdlib_v3 as client
sys.path.insert(0,str(ROOT/'experiments'))
import mc_rc_3d_19series_final_eval_2026_10_07 as original
sys.path.insert(0,str(HERE))
import final_eval_lossless_v3 as revised
np=original.np
def ast_functions(path):return {n.name:n for n in ast.parse(path.read_text(encoding='utf-8')).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
def dump(n):return ast.dump(n,include_attributes=False)
def main():
    sys.stdout.reconfigure(encoding='utf-8');client.resource_guard();original.torch.set_num_threads(1)
    tick=time.perf_counter();OUT.mkdir(exist_ok=False)
    q=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],records=[],
        medical_arrays_loaded=0,model_checkpoint_arrays_loaded_from_disk=0,neural_forwards=0,GPU_forwards=0,
        original_training_modified=False,confirmation_patients_opened=False,lockedIXI_opened=False)
    try:
        build=json.loads((HERE/'BUILD_RECEIPT_V3.json').read_text(encoding='utf-8'));assert build['complete'] and not build['errors']
        for b in build['output_bindings']:assert client.base.entry(ROOT/b['path'])==b
        oldfunc=ast_functions(ROOT/'experiments/mc_rc_3d_19series_final_eval_2026_10_07.py');newfunc=ast_functions(HERE/'final_eval_lossless_v3.py')
        unchanged=[n for n in oldfunc if n not in ['pack_prediction','readiness','frozen_training']]
        for name in unchanged:assert dump(oldfunc[name])==dump(newfunc[name]),name
        packing=copy.deepcopy(newfunc['pack_prediction'])
        changed=0
        for n in ast.walk(packing):
            if isinstance(n,ast.Attribute) and isinstance(n.value,ast.Name) and n.value.id=='np' and n.attr=='savez_compressed':n.attr='savez';changed+=1
        assert changed==1 and dump(oldfunc['pack_prediction'])==dump(packing)
        scientific_names=['numpy_native64','functional_fov','independent_counts','rational_metric','independent_aggregate','trees_close']
        oldverify=ast_functions(ROOT/'experiments/verify_mc_rc_3d_19series_common_init_final_2026_10_07.py');newverify=ast_functions(HERE/'verify_final_lossless_v3.py')
        for name in scientific_names:assert dump(oldverify[name])==dump(newverify[name]),name
        # Equality of evaluator/replay main after reverting only source-binding paths.
        for oldname,newname in [('evaluate_mc_rc_3d_19series_common_init_final_2026_10_07.py','evaluate_final_lossless_v3.py'),
            ('verify_mc_rc_3d_19series_common_init_final_2026_10_07.py','verify_final_lossless_v3.py')]:
            new=(HERE/newname).read_text(encoding='utf-8').replace("HERE/'final_eval_lossless_v3.py'","ROOT/'experiments/mc_rc_3d_19series_final_eval_2026_10_07.py'").replace("HERE/'verify_final_lossless_v3.py'","ROOT/'experiments/verify_mc_rc_3d_19series_common_init_final_2026_10_07.py'")
            before=ast_functions(ROOT/'experiments'/oldname)['main'];after=next(n for n in ast.parse(new).body if isinstance(n,ast.FunctionDef) and n.name=='main')
            assert dump(before)==dump(after),newname
        q['AST_scientific_functions_unchanged']=unchanged+scientific_names+['evaluator_main','independent_replay_main']
        metadata=ROOT/'experiments/mc_rc_3d_19series_final_evaluation_preflight_attempt02_2026_10_07/attempt01.json'
        meta=json.loads(metadata.read_text(encoding='utf-8'));assert meta['complete'] and not meta['errors']
        rows=meta['metadata28_series'];assert len(rows)==28 and 2*sum(v['packed_bytes_per_arm'] for v in rows)==115491840
        largest=max(rows,key=lambda r:np.prod(r['native_shape']))['native_shape']
        real_old_reader=original.unpack_prediction;real_new_reader=revised.unpack_prediction
        def old_memory_reader(handle):handle.seek(0);return real_old_reader(handle)
        def new_memory_reader(handle):handle.seek(0);return real_new_reader(handle)
        original.unpack_prediction=old_memory_reader;revised.unpack_prediction=new_memory_reader
        rng=np.random.default_rng(20261008);jobs=[]
        for shape in [(1,1,1),(1,1,7),(2,3,5),(3,5,7)]:
            for pattern in ['background','foreground','random']:jobs.append((shape,pattern))
        jobs.extend([(tuple(largest),'structured'),(tuple(largest),'random')])
        for shape,pattern in jobs:
            client.resource_guard();assert time.perf_counter()-tick<120
            if pattern=='background':prediction=np.zeros(shape,bool)
            elif pattern=='foreground':prediction=np.ones(shape,bool)
            elif pattern=='random':prediction=rng.integers(0,2,size=shape,dtype=np.uint8).astype(bool)
            else:
                prediction=np.zeros(shape,bool);prediction[tuple(slice(n//4,3*n//4) for n in shape)]=True
            prediction=prediction[::-1,:,::-1];oldbuf=io.BytesIO();newbuf=io.BytesIO()
            started=time.perf_counter();original.pack_prediction(oldbuf,prediction);oldwall=time.perf_counter()-started
            started=time.perf_counter();revised.pack_prediction(newbuf,prediction);newwall=time.perf_counter()-started
            with zipfile.ZipFile(io.BytesIO(oldbuf.getvalue())) as za,zipfile.ZipFile(io.BytesIO(newbuf.getvalue())) as zb:
                assert za.namelist()==zb.namelist()
                assert all(za.read(n)==zb.read(n) for n in za.namelist())
                assert all(i.compress_type==zipfile.ZIP_STORED for i in za.infolist())
                assert all(i.compress_type==zipfile.ZIP_DEFLATED for i in zb.infolist())
            started=time.perf_counter()
            for writerbuf in [oldbuf,newbuf]:
                for reader in [real_old_reader,real_new_reader]:
                    writerbuf.seek(0);assert np.array_equal(reader(writerbuf),prediction)
            readerwall=time.perf_counter()-started
            n=int(prediction.size);p=np.packbits(prediction.reshape(-1),bitorder='little')
            assert p.nbytes==(n+7)//8
            if n%8:assert int(p[-1])>>(n%8)==0
            q['records'].append(dict(shape=list(shape),pattern=pattern,noncontiguous=not prediction.flags.c_contiguous,
                voxels=n,raw_packed_bytes=int(p.nbytes),uncompressed_NPZ_bytes=len(oldbuf.getvalue()),compressed_NPZ_bytes=len(newbuf.getvalue()),
                compressed_to_uncompressed_ratio=len(newbuf.getvalue())/len(oldbuf.getvalue()),
                uncompressed_write_and_selfcheck_seconds=oldwall,compressed_write_and_selfcheck_seconds=newwall,
                four_cross_reads_seconds=readerwall,npy_members_byte_identical=True,all_four_cross_reader_checks_passed=True,
                unused_padding_bits_zero=True,synthetic_input_not_MRI=True))
            oldbuf.close();newbuf.close();del prediction,p
        original.unpack_prediction=real_old_reader;revised.unpack_prediction=real_new_reader
        q.update(complete=True,all_lossless_interoperability_checks_passed=True,synthetic_payloads=14,total_cross_reader_checks=56,
            metadata28_identity_checked=True,uncompressed_56_payload_bytes=115491840,
            largest_real_native_shape_metadata=largest,actual_MRI_compression_bytes_measured=False,
            original_readers_not_modified_on_disk=True,only_BytesIO_seek_adapter_used_in_qualification=True,
            production_bindings=[client.base.entry(p) for p in [HERE/'final_eval_lossless_v3.py',HERE/'evaluate_final_lossless_v3.py',
                HERE/'verify_final_lossless_v3.py',HERE/'PROTOCOL.md',HERE/'REPAIR_V3.md']]+[r['original'] for r in build['records']],
            source_bindings=[client.base.entry(p) for p in [Path(__file__),HERE/'BUILD_RECEIPT_V3.json',metadata]],
            resource_snapshot=client.resource_guard())
    except Exception as e:q['errors'].append(repr(e));q['traceback']=traceback.format_exc()
    q['elapsed_seconds']=time.perf_counter()-tick;client.base.new(OUT/'receipt.json',q)
    print(json.dumps(dict(complete=q['complete'],errors=q['errors'],synthetic_payloads=len(q['records']),
        realistic_shape_records=q['records'][-2:],resource_snapshot=q.get('resource_snapshot')),ensure_ascii=False),flush=True)
    return int(not q['complete'])
if __name__=='__main__':raise SystemExit(main())
