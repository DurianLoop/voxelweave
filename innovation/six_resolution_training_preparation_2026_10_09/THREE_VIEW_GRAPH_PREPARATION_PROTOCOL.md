# 三视图保留attached均值的图准备：人工输入，非医学资格

固定原CheckpointedTaskUNet3D/深监督binary loss、原参数名/算子，采用两sample人工16×16×16 patch，仅作三视图完整图语义检查，不把小patch代实际64×128×128或19series资格。两个共同初始化模型，packed一次batch6 forward vs三次batch2 sequential forward；每视图用已验证GIN参数生成且不改target。监督第一份视图；最终head构造softmax([0,z])，三视图attached mean-target reverse-KL，element mean，人工检查lambda0.1，不认定医学lambda已选择。

每模型保留全部三视图图后一次backward，checkpoint recomputation保持原语义；比较三head概率、总loss及全部对应参数gradient，阈值3e-6；零Grad/None逐项保留。两步共同人工views序列、AdamW lr/decay1e-4、betas(.9,.999)/eps1e-8/foreachFalse/fusedFalse，若optimizer之后参数差超过3e-6，保留失败，不放宽。optimizer states/moments只检查记录数值差，不把人工qualification冒称医学228更新。

CPU1/interop1/below-normal、RAM/disk8GB，preparation7MB/FOV20MB/other22.8MB完整余量，wall180秒。CUDA不可见且不得初始化；不读MRI/GT/父模型、未见确认/lockedIXI，不保存人工checkpoint，不操作原训练/其他PID。模型与合成target仅本进程新建内存；只有小receipt。GPU整batch与sequential实际显存/时间、所有19series、母GT/geometry仍须另冻资格，不能由本次passed推断2.5GB符合。
