# 释放已经用完的skip引用，模型数学不变

原fullpatch独立v1 actual389141 exit1：三路forward完成，step0 GPU反向在checkpoint重算norm创建256MiB输出时OOM，CPU/optimizer均0，原失败保持。cost一次成功不能替代两步对照；可能的常驻input与分配碎片不能凭文字当确认原因。

新compact model v2只改变Python张量引用生存期：encoder只将前三个skip保留列表，decoder按pop消耗skip，在拼接完成后del skip与旧up输出，checkpoint返回后del merged。仍同module conv/norm/activation、FP64计算、54FP32参数与disjointpool。新运行将GPU人工view逐个临时传输，不常驻三路input；CPUview不变。不改变图梯度或数学、patch/通道/预算。

先同16³两步GPU对独立CPU functional原全部54/162与概率binary3e-6/0 gate，CPU保存hooks仍逐位核查；通过后原64x128x128三view两步对独立CPU，wall10800。失败随时保留，不降cap/eps/门槛。不初始化医学数据、不动用户进程。
