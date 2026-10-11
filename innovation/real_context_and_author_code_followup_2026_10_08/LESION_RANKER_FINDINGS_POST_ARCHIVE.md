# 作者所链 ranker 已读，但不能替代 OOF 或集成实现

本文件为主归档真正77256b exit0之后的追加，不修改旧冻结文件。2026作者稿 PMC13148016所链仓库的公开HEAD固定到 `ecd3b9bdadc40877b9832ea49b5c82d5e27e7d14`，取得源码和README，不clone或执行作者代码。entry63a23b和ranker source d73d9c均真正exit0；README未截断891d5e，ranker.py全部162行未截断aaf3f0。作者稿41–49块747e2b为定向重读，不新增不同论文数量。

README明确说明它是**unofficial re-implementation**，不保证与官方BraTS分数相同。README引述DSC+HD95的6排名，当前ranker.py90却取每region的Dice、NSD1.0、NSD0.5三个平均rank；不能直接把它叫做官方HD95排名实现，也不能以公开HEAD代替2026论文实际运行版本。

ranker.py22–57逐位置比较不同submission同index的分数，较高较好，平局采用dense rank（如1,1,2），不是competition 1,1,3。130–152只读取CSV、删Num开头列、转to_list按行位置排名；仅查长度相等，不按患者身份join或检查顺序。用于本项目必须先认证完整患者分母、patient/series ID和行序一致，不能凭同样行数认定配对正确。举例：同患者配对A=(.9,.6)、B=(.8,.5)时A两个病人都胜出；只把B的两行交换就会变成一胜一负，数据值没变、排名结论改变。这个是输入契约的数学例子，没有执行作者实现或患者评分。

59–111在各region及所有region平均后选择最低rank的**固定最佳模型**。全部文件未实现 patient-specific selector、模型训练、5fold划分、OOF预测生成、ensemble weight、概率组合或CC后处理；所以现有源码只补齐ranker语义，未解决正文“averaged 5-fold output”在训练病例上的OOF身份或Table1权重归一化。没有据此宣称作者发生数据泄漏或方法错误；缺的是可以核实的实际训练/ensemble/预测记录。

按前轮公式文本解读，若Wi=(S-Fi)/S，M个候选权重总和是M-1；3模型即2，而Table1每列和为1。这需要真实ensemble源码/公式布局/勘误确定额外归一化，ranker不含该代码，不能任意补出作者实现。统一正比例不改变多类argmax，但改变概率阈值/校准等，因此复现时必须明确。当前重读未消除该缺口。

对创新定位：将region metric ranker或static best submission称作新策略不成立。部署时预测**具体动作的患者损害差及全费用**，则需要严格折外监督的actual action labels、GT-free特征和合法初始化；仅排序Dice/NSD或用GT radiomics分群不构成它。现有11开发GT训练parent仍不可冒充外折初始化；8未见确认/lockedIXI保持关闭。

来源字节和响应：[entry receipt](lesion_ranker_entry_attempt01/receipt.json)、[source receipt](lesion_ranker_source_attempt01/receipt.json)。此新增源码162行与README属于主provenance3970行之后的追加，不覆盖历史数量/reading=false；后续追加登记记录为FastSurfer3970行+ranker162行共4132行源码，README另计。
