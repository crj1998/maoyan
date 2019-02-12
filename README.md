猫眼反反爬——css反爬解析
====
# 一、概述
有爬虫，就一定会有反爬虫，也因此一定会有反-反爬虫，双方就是在不断变换策略，但是，只要是是使用代码实现的，也一定会有用代码破解的办法。爬虫终究会战胜反爬虫。

此次就是使用python应对猫眼电影的CSS字体反爬措施，以 [影片总票房排行榜页](https://piaofang.maoyan.com/rankings/year)为例，分析并破解猫眼对数据的加密，从而获得票房数据。  

> 所需要的软件和字体文件均在[百度网盘](https://pan.baidu.com/s/1BBLdT_VMcfzYUsrVFahyiQ)中，提取码`3qu6`。
> 代码在我的[GitHub](https://github.com/crj1998/maoyan)上


# 二、反爬分析
用户可以看到的总票房界面如下，看这样式，要么是一个表格`table`标签或者是无序列表`ul`标签，爬取不是问题。
![前端页面](https://upload-images.jianshu.io/upload_images/13843118-7c2ce3012c577e1d.PNG?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
使用`F12`的`Element`界面选择一个数据，但是看到的却是方块。
![F12](https://upload-images.jianshu.io/upload_images/13843118-387dc266719758c6.PNG?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
由于`Element`界面会对页面进行一些解析，不是最原始的页面，需要查看源代码![源代码](https://upload-images.jianshu.io/upload_images/13843118-de150a498fd3bddc.PNG?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
熟悉前端的话，对以`&`开头的应该不陌生，这是转义字符，说明我们能够直接在网页中看到的是进过某种“编码”后的数字。
再回到`Element`界面，将红圈中的两个红圈中的钩去掉，则可以看到页面中的数据变为方框了，由基础的CSS知识可知，这里猫眼使用了一种自定义的字体`cs`，点击一下`year:39`就可以找到字体的定义了。
![font](https://upload-images.jianshu.io/upload_images/13843118-ecd171ed9dd5beaf.PNG?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
![font-url](https://upload-images.jianshu.io/upload_images/13843118-38a008ff43b4c9f2.PNG?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
可以将`url`括号中的复制到浏览器中，转到后会下载一个`下载.woff`文件（什么是["WOFF文件"](https://baike.baidu.com/item/WOFF/10623561)？），即一个开放字体，但是打开该文件需要专用的软件[**FontCreator**](http://www.mydown.com/soft/359/509448859.shtml)，将woff文件导入后，看到如下界面
![fontcreater](https://upload-images.jianshu.io/upload_images/13843118-a269dbe46a559fbc.PNG?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
比如战狼2的场均人次为38，而源代码中为`&#xe0b4;&#xe800;`上图中38为`uniE0B4 uniE800`，规律显而易见，其他的亦是如此。也就是说只要找到代码与数字的映射关系就可以获取数据，看上去很简单，**但是**是不是源码数字的映射就一种呢？刷新一下界面，发现源码竟然变了。
![source_code](https://upload-images.jianshu.io/upload_images/13843118-5f2c4000fe2e8107.PNG?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
重复上述步骤，可以发现woff文件中，数字对应的编码也改变了，也就是说，虽然显示的是一样的，但是相同的数字对不同的`src:url()`中的编码是不一样的，想要解决这一问题，就要从字体实现的角度来分析。比如7虽然对不同的文件有不同的编码，但是无论什么编码其表示都是先横再斜下来，也就是说如果用坐标表示的话，他们的坐标是一样的，可以先选择一个标准对照组，找到数字-编码-坐标对应关系，对于其他的字体文件，如果坐标和标准对照组中的坐标一样，则意味着两个表示的是同一个数字，由于对照组的对应关系已知，则该字体的对应关系也可推得。在python中，这就需要借助`fontTools`库。  

# 三、代码实现
首先是建立一个标准对照组

	# 选择一个标准字体对照表
	standardFont = TTFont("standard_font.woff")
	# 使用 "FontCreator字体查看软件" 查看字体的对应关系，然后设置对应关系
	standardNumList = ["1", "6", "8", "0", "3", "4", "7", "5", "9", "2"]
	standardUnicodeList = ["uniE3CA", "uniF2E0", "uniE667", "uniF6F5", "uniE123","uniF778", "uniE373", "uniF214", "uniE7BB", "uniF19C"]

由于字体是base64，可以直接使用base64解码为woff文件。代码涉及到`fontTools`库的使用，具体使用可以参考官方文档。

	# 字体解析，参数为url中的base64，record为是否保存中间文件
	# 返回对照关系
	def parse_font(s, record=False):
	    data = base64.b64decode(s)
	    maoYanFont = TTFont(io.BytesIO(data))
	    if record:
	        font.saveXML("maoyan.xml")
	        font.save("maoyan.woff")
	        # maoYanFont = TTFont("maoyan.woff")
	    maoYanUnicodeList = maoYanFont["cmap"].tables[0].ttFont.getGlyphOrder()[2:]
	    comparisonTable = {".": "."}
		
		# 外层循环是遍历输入字体的每个数字，对每个数字，去标准对照组中寻找相同坐标的对应的数字
		# maoYanGlyph、baseGlyph可以看作是字体的坐标
	    for i in range(10):
	        maoYanGlyph = maoYanFont["glyf"][maoYanUnicodeList[i]]
	        for j in range(10):
	            baseGlyph = standardFont["glyf"][standardUnicodeList[j]]
	            if maoYanGlyph == baseGlyph:
	                comparisonTable[maoYanUnicodeList[i][3:].lower()]=standardNumList[j]
	                break
	    return comparisonTable

至于页面的爬取，字体base64的获取相对较简单，但是注意，python大部分库解析html页面时，对`&`开头的会解析为unicode，例如`&#xe0b4;`解析为`\ue0b4`需要使用`repr`函数将其转为原始字符串再对应。

# 四、总结
爬虫本质上是利用HTML是一种标记语言的特性，因此想要深入掌握爬虫，必须对前端`HTML+CSS+JS`有一定的了解，无需掌握透彻，只需要能够大概知道实现原理即可。比如猫眼的CSS反爬不过是使用CSS的字体而已。