### 语音识别：音乐类型区分
#### 特征一：过零率
> 该特征在语音识别和音乐信息检索中都被大量使用
> 对于像金属和岩石那样的高冲击声，它通常具有更高的值。
>
#### 特征二：光谱质心
> 它指示声音的“质心”位于何处，并计算为声音中存在的频率的加权平均值。
> 如果有两首歌曲，一首来自布鲁斯类型，另一首属于金属。
> 与长度相同的布鲁斯流派歌曲相比，金属歌曲在最后有更多的频率。
> 因此，布鲁斯歌曲的光谱质心将位于其光谱中间附近，
> 而金属歌曲的光谱质心将朝向它的末端。
>
#### 特征三：光谱衰减
> 是信号形状的度量
>
#### 特征四：梅尔倒频谱系数
> 信号的Mel频率倒谱系数（MFCC）是一小组特征（通常约10-20），
> 其简明地描述了频谱包络的整体形状，
> 它模拟了人声的特征。
>
#### 特征五：色度频率
> 色度频率是音乐音频有趣且强大的表示，
> 其中整个频谱被投影到12个区间，
> 代表音乐八度音的12个不同的半音（或色度)