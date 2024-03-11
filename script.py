import re
import sqlite3

from utils.global_utils import RULE_DB_PATH

input_text = """
客户ID,客服ID,消息内容,发送方,发送时间,对话ID
客户1,客服1,你们公司的产品质量怎么样?我看到有些差评说很一般。,1,2023/10/16 14:00,1
客户1,客服1,您好，非常感谢您的疑问。我们公司一直非常重视产品质量，任何质量问题都会受到高度重视并及时改正。如果您在使用过程中遇到任何问题，欢迎随时反馈给我们。,0,2023/10/16 14:05,1
客户1,客服1,那好吧，不过我还是有点担心。你能保证如果我购买后出现问题，可以无条件退换吗?,1,2023/10/16 14:10,1
客户1,客服1,当然可以，我们有完善的售后服务体系，只要是我们公司产品的质量问题，都可以无条件退换。亲爱的客户请放心购买。,0,2023/10/16 14:15,1
客户2,客服2,你好，我最近买的这款产品有个功能用不了。,1,2023/10/17 11:20,2
客户2,客服2,非常抱歉给您带来了不便，请问是哪个功能无法使用呢?您可以描述下具体情况吗?,0,2023/10/17 11:25,2
客户2,客服2,就是它的无线连接功能，我按说明操作后就是没反应。,1,2023/10/17 11:30,2
客户2,客服2,了解了，谢谢详细描述。那个无线连接功能确实比较容易出现连接失败的问题，我建议您可以先尝试重启设备，或检查下无线网络信号是否正常。如果还是无法连接，欢迎拨打我们的售后热线，工作人员会远程为您诊断和解决。,0,2023/10/17 11:35,2
客户3,客服3,我想换一下你们的其他产品，这个用起来还是有些不习惯。,1,2023/10/18 16:40,3
客户3,客服3,好的尊敬的客户，请问您需要换成我们哪一款产品呢?我这边可以为您比较一下不同型号的参数配置，确保更换后能完全满足您的需求。,0,2023/10/18 16:45,3
客户3,客服3,嗯，就是你们最新上市的那款吧，听说性能不错。,1,2023/10/18 16:50,3
客户3,客服3,了解了，您说的应该是我们最新款的XX型号。它在CPU、内存、续航等各方面的确有了非常大的提升，是目前我们旗舰级产品。如果您对其性能、使用体验等有任何疑问，我都可以为您详细解答。,0,2023/10/18 16:55,3
客户4,客服4,您好,我最近购买了你们公司的产品,总体还可以,就是有一些小瑕疵。,1,2023/11/20 09:30,4
客户4,客服4,非常抱歉给您带来了不佳的体验。能否详细描述一下您遇到的问题呢?我们一定会及时改正。,0,2023/11/20 09:35,4
客户4,客服4,嗯,就是外观有些划痕,而且无线连接也不太稳定。我对这个产品还是比较失望的。,1,2023/11/20 09:40,4
客户4,客服4,太抱歉了,我完全理解您对产品质量的不满。我们将立即反馈给相关部门,尽快优化产品质量。作为补偿,我这边可以为您免费更换一台新机,并享受折扣优惠购买其他配件。还请您多多包涵。,0,2023/11/20 09:45,4
客户5,客服5,你好,我看了你们最新的产品介绍,感觉很不错。但是我对哪款更合适还是比较迷茫的。,1,2023/11/21 14:10,5
客服5,客户5,非常感谢您对我们产品的关注。不知您主要是用于什么场景呢?根据您的使用需求,我可以为您推荐最合适的型号。,0,2023/11/21 14:15,5
客户5,客服5,主要是家庭日常使用,需要性能稳定一些,其他没有太多特殊要求。,1,2023/11/21 14:20,5
客服5,客户5,了解了,根据您的需求,我给您推荐我们的XX款吧。这款采用了行业顶级的芯片,运行内存也比较大,能够确保长期稳定高效的使用体验。而且做工精细、外观时尚,非常适合家庭使用场景。您可以考虑下这个型号。,0,2023/11/21 14:25,5
客户6,客服6,你们的售后服务怎么样?有没有七天无理由退货政策?,1,2023/11/22 16:45,6
客服6,客户6,亲爱的客户您好,我们一直非常重视售后服务工作。所有产品都享受15天无理由退货,90天免费保修的政策。如果在使用过程中出现任何质量问题,我们也会及时免费维修或者换新。,0,2023/11/22 16:50,6
客户6,客服6,那太好了,之前在别的商家遇到过退货很麻烦的情况,希望你们这边不会那样。,1,2023/11/22 16:55,6
客服6,客户6,完全不会的,退货流程非常简便。只需要准备好购买凭证和完好包装箱,通过快递将产品寄回我司即可,费用也由我们承担。售后人员会及时为您办理退货手续,给您一个满意的答复。,0,2023/11/22 17:00,6
客户7,客服7,你们公司最新的那款笔记本电脑评价怎么样?值得入手吗?,1,2023/11/23 10:15,7
客服7,客户7,这款新品的综合表现确实非常出色。作为我们旗舰产品,CPU、显卡等硬件配置都是行业顶级,能轻松满足各类办公和娱乐需求。此外,全金属机身、长待机、超窄边框等人性化设计也获得了业界一致好评。,0,2023/11/23 10:20,7
客户7,客服7,听起来很不错,不过价格是不是有点高啊?,1,2023/11/23 10:25,7
客服7,客户7,您提出了一个非常好的疑问。虽然售价确实比普通机型偏高一些,但相比其硬件规格和人性化体验来说,性价比其实很高。更重要的是,我们正在针对这款新品推出优惠政策,如果在本月内购买将享受8折优惠,费用已经更加亲民了。,0,2023/11/23 10:30,7
客户8,客服8,您好,我是不是可以现在就立即下单?这款新品现在有现货吗?,1,2023/11/24 14:40,8
客服8,客户8,尊敬的客户您好,非常感谢您对我们产品的青睐。这款新品现在全国范围内都有现货供应,如果您现在就下单的话,将在1-3个工作日内为您发货。,0,2023/11/24 14:45,8
客户8,客服8,好的,那我现在就在网上下单了,这个新品太让我心动了。,1,2023/11/24 14:50,8
客服8,客户8,非常感谢您的订购!这绝对是一个正确的选择。我们将迅速为您处理订单,并确保产品状态良好。再次感谢您的支持与厚爱,祝您使用愉快!,0,2023/11/24 14:55,8
客户9,客服9,你好,我昨天购买了你们的新手机,现在已经收到了。有什么要注意的吗?该怎么激活使用?,1,2023/11/25 11:10,9
客服9,客户9,您好,非常感谢您选购我们的新品手机!使用前的准备工作非常简单。首先请取出手机和电源适配器,给电池充满电。然后按下电源键开机,根据屏幕指引完成初始设置即可。如果在操作过程中有任何疑问,欢迎随时咨询我们。,0,2023/11/25 11:15,9
客户9,客服9,好的,谢谢您的指导。对了,这款新机的拍照功能应该如何使用?能详细介绍一下吗?,1,2023/11/25 11:20,9
客服9,客户9,非常感谢您对我们手机拍照功能的关注。这款新机拥有业界顶级的AI智能相机系统,其人像模式、夜景、美颜等拍照功能都处于领先水平。您只需打开相机应用,根据场景选择对应模式即可,非常简便易用。我这里还有详细的拍照攻略,需要的话可以发给您。,0,2023/11/25 11:25,9
客户10,客服10,我对你们新上市的平板电脑还是比较感兴趣的,不过实体店看了下貌似和宣传的不太一样。实体店的那个款式到底怎么回事? ,1,2023/11/26 15:35,10
客服10,客户10,非常感谢您对我们新品平板电脑的关注。根据您的描述,我判断您可能看到了我们之前发布的某一款样机。新品与样机在细节上的确有一些区别,不过大体方案是没有改变的。具体规格配置可以参考我们官网或者实体店介绍。,0,2023/11/26 15:40,10
客户10,客服10,那这个新品到底有什么亮点?和其他品牌有何区别?您老给我分析分析吧。,1,2023/11/26 15:45,10
客服10,客户10,好的,我这就为您详细介绍一下。我们这款新品平板电脑最大的特点就是集高端和极致轻薄于一体。采用了行业顶级的芯片和大容量内存,但机身仅4.8毫米超薄,重量不足300克。应用体验丝毫不输台式机。此外,独特的三防设计可以防尘防水防摔。再加上超长待机等黑科技,真正将性能和便携融合得天衣无缝。,0,2023/11/26 15:50,10
客户11,客服11,最近看到你们新推出的智能音箱,想请教下使用体验如何?,1,2023/11/27 09:25,11
客服11,客户11,非常感谢您对我们新品的关注。这款智能音箱不仅音质出众,支持无损音频解码,而且语音交互体验也相当人性化。它能够精准识别语音指令,对多种复杂命令都可以快速理解和执行,无论是音乐播放、天气查询还是在线购物,使用都非常便捷。,0,2023/11/27 09:30,11
客户11,客服11,听起来很不错,不过据说续航时间比较短?这个问题有没有得到改善?,1,2023/11/27 09:35,11
客服11,客户11,您提出了一个好问题。此前早期版本的确存在电池续航有限的问题。但我们最新的这一代智能音箱已经在电池容量和待机耗电上做了全面升级,使用3-4周无需充电完全无压力。即便长期使用也一定能给您留下极佳的用户体验。,0,2023/11/27 09:40,11
客户12,客服12,不知这次你们新手机的拍照功能如何?我是一个比较喜欢摄影的人。,1,2023/11/28 14:10,12
客服12,客户12,新机的影像系统绝对是一大看点。我们不仅在硬件上采用了新一代AI超级夜视相机,支持夜景视频防抖等黑科技,软件算法方面也做了大量人性化优化,肖像渲染、长曝光、美颜美肤等功能都领先同行。即便是在夜间或是阴暗环境,相机依然能捕捉高质量的细节。,0,2023/11/28 14:15,12
客户12,客服12,听起来很让人期待,不过这样高端的相机配置售价应该很高吧?对于一般消费者来说能承受得了吗?,1,2023/11/28 14:20,12
客服12,客户12,关于这一点请您放心。我们在定价时非常注重性价比,绝不会让普通用户觉得太贵。实际上,新机的公司指导价已经比市面上同等配置的产品便宜不少。而且我们还推出了分期免息和老用户优惠等政策,让更多人都能体验到旗舰影像的乐趣。,0,2023/11/28 14:25,12
客户13,客服13,你好,我最近购买了你们的新款笔记本电脑,结果出现了一些故障。具体是开机就自动重启,一直循环这个过程。,1,2023/11/29 10:35,13
客服13,客户13,非常抱歉给您带来了这么大的不便,我们一定会尽快协助您解决。能否请您描述一下具体使用的是哪个型号?是否也可以将故障现象拍个视频发给我,方便我们分析原因。,0,2023/11/29 10:40,13
客户13,客服13,好的,是XXXX型号的,视频我这就拍一段发给你。不过现在这个状况我根本没法正常使用机器,我是想尽快换一台新的,行吗?,1,2023/11/29 10:45,13
客服13,客户13,确实,我们会优先考虑为您更换一台新机。请您将故障描述、视频和购买凭证一并发给我,我们会立即着手为您办理新机更换手续。如果在这个过程中遇到任何其他问题,也尽管继续反馈给我们。确保让您早日使用上全新的笔记本,我们将不惜一切代价。,0,2023/11/29 10:50,13
客户14,客服14,你们公司新推出的平板电脑我在上个月就预订了,但一直没收到,已经快1个多月了,发货情况怎么样?,1,2023/11/30 16:25,14
客服14,客户14,非常感谢您的谅解与等待。这款新品平板电脑自上市以来反响热烈,订单量超出了我们的预期,所以出现了发货延迟的情况。但请放心,我们已经大量加紧供货。根据我手上的信息,您的订单预计将在3-5个工作日内发出。实在给您带来诸多不便,我们会优先处理您的订单,并为您提供相应的延误补偿。,0,2023/11/30 16:30,14
客户14,客服14,3-5天的话还好,只要别再拖就行。不过你们也应该好好改进一下供货和发货的效率,要不就是损失大量潜在客户。,1,2023/11/30 16:35,14
客服14,客户14,您说得非常有道理,我们确实在这方面做得还不够好。我已将您的宝贵意见反馈给了上级,我们会从供应链、物流等多方面着手优化,尽最大努力避免类似延期情况再次发生。作为对您的补偿和道歉,您的订单将免费享受顺丰特惠服务,确保快递时效。希望您多多谅解。,0,2023/11/30 16:40,14
客户15,客服15,你们公司的新款无线耳机怎么样?音质和防水表现如何?,1,2023/12/1 11:10,15
客服15,客户15,非常感谢您对我们新品无线耳机的关注。这款耳机采用了独家开发的混合主动降噪技术,能最大程度滤除外界噪音,还原出原汁原味的高品质音效。此外,它还通过了IP67级别的严苛防水测试,即便在户外下雨天也可以放心佩戴使用。无论是通勤通话还是户外运动,这款耳机都能给您带来极佳的体验。,0,2023/12/1 11:15,15
客户15,客服15,听起来很不错,不过续航时间够用吗?我平时也是经常需要长时间使用。,1,2023/12/1 11:20,15
客服15,客户15,您提出了一个非常好的疑虑。这款耳机的续航表现同样出色,单次使用可达8小时,再配合便携式充电盒使用,总待机时间高达24小时。即便是户外长途旅行,也完全可以满足您的使用需求。当然,如果您对续航时间仍有其他疑问,我这里还有详细的电池数据资料,随时欢迎您查阅。,0,2023/12/1 11:25,15
客户16,客服16,你们最新款的智能电视盒子是否支持4K分辨率?系统界面简洁吗?,1,2023/12/2 14:40,16
客服16,客户16,是的,我们最新一代的智能电视盒子完全支持目前最高的4K超高清分辨率,色彩还原和细节层次都达到了业界领先水平。同时,我们也在系统界面方面下了很大功夫,通过精简布局和人性化设计,使操作变得前所未有的直观简洁。即便是老年人也能快速上手,无需花太多精力学习使用。,0,2023/12/2 14:45,16
客户16,客服16,听起来很不错啊。那请问这款盒子的接口是否足够多?我有很多外设需要连接。,1,2023/12/2 14:50,16
客服16,客户16,完全不用担心这个问题。我们在硬件接口方面一直非常用心,除了标配的HDMI、网口等基础接口外,还提供了3个USB3.0接口以及无线投屏功能。您完全可以同时连接游戏手柄、硬盘、键盘等多种外设,完美满足各种使用场景。毕竟这也正是我们的初衷所在,为用户打造高度智能且联网性极强的家庭影音中心。,0,2023/12/2 14:55,16
客户17,客服17,你好,最近在论坛上看到有人反馈你们最新的笔记本电脑出现了自动重启的故障,这到底是什么情况?是硬件还是系统问题?我最近也在考虑购买那款机型,所以非常在意这个问题。,1,2023/12/3 10:15,17
客服17,客户17,非常感谢您的提醒。我们对于那个自动重启的反馈确实高度重视,并已着手紧急调查和修复。初步判断,导致这一故障的主要原因是某一细小硬件驱动的兼容性问题,但整体上我们的产品质量完全没有任何疑虑。所有符合条件的用户,我们都将为其免费更换新品或提供相关的补救措施。,0,2023/12/3 10:20,17
客户17,客服17,那就好,希望你们能尽快全面解决这个问题。既然如此,那我对这款笔记本是否还值得购买也就没有那么多疑虑了。,1,2023/12/3 10:25,17
客服17,客户17,非常感谢您的谅解,我们一定会尽快彻底解决这一问题。这款笔记本是我们公司今年的重点产品,无论是硬件配置还是系统体验都代表了我们的最新科技水平,大可放心选购。当然,如果您对任何细节有疑问,我们的技术人员也可以在购买前为您进一步解答。,0,2023/12/3 10:30,17
客户18,客服18,你们公司的新款智能手表上市了吗?听说它的健康监测功能很强大,我很感兴趣想入手。,1,2023/12/4 15:50,18
客服18,客户18,是的,这款集健康监测于一身的智能手表已经在上周正式上市开售了。您对它的关注非常正确,它搭载了多项全新的健康科技,可以实现24小时不间断监测心率、睡眠、血氧等多种身体数据。此外,它还支持多种户外运动模式和精准卫星定位导航,对于运动爱好者来说也是非常实用。,0,2023/12/4 15:55,18
客户18,客服18,听起来很不错啊。这手表的续航时间够用吗?我可能要长时间佩戴使用它,如果电池太快没电就不方便了。,1,2023/12/4 16:00,18
客服18,客户18,您提出了一个非常好的疑问。这一代手表在电池寿命方面我们做了诸多优化,单次充电可使用7天以上,日常使用完全足够。即便是开启了所有监测功能,也至少可使用48小时以上。更重要的是,它还支持无线快充,只需15分钟就可以恢复大半的电量,补给非常方便。综合续航和快充来看,它绝对能满足您长期佩戴的需求。,0,2023/12/4 16:05,18
客户19,客服19,你好,我最近购买了你们的新款平板电脑,但是在使用时出现了一些问题。就是偶尔会无故发生系统死机,甚至一度无法重启,这种情况持续了好几次了。,1,2023/12/5 11:20,19
客服19,客户19,非常抱歉给您的使用带来了这么大的不便,我们一定会高度重视并及时协助解决。能否请您描述一下具体的死机现象?比如是在什么情况下发生、有无报错提示等,并将相关日志和截图发给我一份。只要掌握了问题根源,我们就可以有的放矢地进行修复。,0,2023/12/5 11:25,19
客户19,客服19,好的,我这就尝试录制一个视频给你。不过这简直让人抓狂,我当初购买的目的就是为了高效办公,现在频繁死机影响太大了,能否先给我换一台新的设备?我实在等不及修复。,1,2023/12/5 11:30,19
客服19,客户19,我完全理解您的心情,出现这种故障确实影响太大了。为了最大程度消除您的后顾之忧,我这边现在就为您启动新机更换流程,您尽管将故障信息发给我备案就好。新平板一旦到货,我们将火速为您免费更换,绝不延误。同时我们也会继续跟踪故障原因,努力避免同类问题再次发生。,0,2023/12/5 11:35,19
"""
# Split the input text into lines for processing
lines = input_text.strip().split("\n")

# Define a pattern to match records and a subpattern for the "消息内容" field
record_pattern = re.compile(r'^([^,]+,[^,]+,)([^,]+)(,.+)$')


# Function to replace Chinese commas within the "消息内容" field only
def replace_commas_in_message_content(text):
    lines = text.strip().split('\n')  # Split the input text into lines
    processed_lines = [lines[0]]  # Add the header line as it is

    for line in lines[1:]:  # Skip header line
        fields = line.split(',')  # Split each line into fields based on commas

        # The "消息内容" field can be found at index 2, but since there might be commas within the field itself,
        # we need to handle this carefully Reconstruct the "消息内容" field considering that it might have been split
        # incorrectly due to internal commas
        message_content = ','.join(
            fields[2:-3])  # Rejoin the message content, assuming the last 3 fields are always "发送方,发送时间,对话ID"
        message_content_replaced = message_content.replace(',',
                                                           '，')  # Replace commas with Chinese commas in the message
        # content

        # Reassemble the line with the updated message content
        new_line = ','.join(fields[:2] + [message_content_replaced] + fields[-3:])
        processed_lines.append(new_line)

    return '\n'.join(processed_lines)  # Join the lines back together into a single string


print(replace_commas_in_message_content(input_text))
