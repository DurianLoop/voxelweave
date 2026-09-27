# geometry full 判定

control：64轮早停，best epoch49，25.5620114752 dB。
geometry：57轮早停，best epoch42，25.5641375251 dB。

23名validation患者配对增益+.0021260498 dB；10,000次bootstrap 95% CI[-.0002293948,+.0057160560]；13/23胜。

未通过：效应≥+.08、CI下界>0、至少60%患者获胜。通过：parent最差四分位方向、其他均值质量、forward时间与显存比例。**总判定不晋级。** 不将均值微小改善当作结构收益，不继续旧geometry累加链。

报告生成发现旧report的NumPy布尔值无法直接JSON编码；本次仅在输出时将NumPy标量转为Python标量，配对公式/门槛未改，旧源码保持原样以便验证已完成run的哈希。

下一独立假设见 `design/pastnet_v2_independent/PROTOCOL_ZH.md`：只验证基于已有索引/phase信息的多尺度空间对应，不带geometry、不从geometry best初始化。其源码与协议单独入manifest，复用哈希核验通过的原control作为预算匹配对照。
