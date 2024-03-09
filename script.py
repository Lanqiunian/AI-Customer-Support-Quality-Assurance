import json
import re
import sqlite3

from services.db_rule import add_rule
from services.rule_manager import Rule
from utils.file_utils import TASK_DB_PATH

import csv

input_text = """
客户1,客服1,你们公司的产品质量怎么样?我看到有些差评说很一般。,1,2023/10/16 14:00,1
客户1,客服1,您好,非常感谢您的疑问。我们公司一直非常重视产品质量,任何质量问题都会受到高度重视并及时改正。如果您在使用过程中遇到任何问题,欢迎随时反馈给我们。,0,2023/10/16 14:05,1
客户1,客服1,那好吧,不过我还是有点担心。你能保证如果我购买后出现问题,可以无条件退换吗?,1,2023/10/16 14:10,1
客户1,客服1,当然可以,我们有完善的售后服务体系,只要是我们公司产品的质量问题,都可以无条件退换。亲爱的客户请放心购买。,0,2023/10/16 14:15,1
客户2,客服2,你好,我最近买的这款产品有个功能用不了。,1,2023/10/17 11:20,2
客户2,客服2,非常抱歉给您带来了不便,请问是哪个功能无法使用呢?您可以描述下具体情况吗?,0,2023/10/17 11:25,2
客户2,客服2,就是它的无线连接功能,我按说明操作后就是没反应。,1,2023/10/17 11:30,2
客户2,客服2,了解了,谢谢详细描述。那个无线连接功能确实比较容易出现连接失败的问题,我建议您可以先尝试重启设备,或检查下无线网络信号是否正常。如果还是无法连接,欢迎拨打我们的售后热线,工作人员会远程为您诊断和解决。,0,2023/10/17 11:35,2
客户3,客服3,我想换一下你们的其他产品,这个用起来还是有些不习惯。,1,2023/10/18 16:40,3
客户3,客服3,好的尊敬的客户,请问您需要换成我们哪一款产品呢?我这边可以为您比较一下不同型号的参数配置,确保更换后能完全满足您的需求。,0,2023/10/18 16:45,3
客户3,客服3,嗯,就是你们最新上市的那款吧,听说性能不错。,1,2023/10/18 16:50,3
客户3,客服3,了解了,您说的应该是我们最新款的XX型号。它在CPU、内存、续航等各方面的确有了非常大的提升,是目前我们旗舰级产品。如果您对其性能、使用体验等有任何疑问,我都可以为您详细解答。,0,2023/10/18 16:55,3
客户4,客服4,你们公司的服务真是太差劲了,我已经打了几次电话都没人回复,究竟是什么原因?,1,2023/10/19 09:15,4
客户4,客服4,非常抱歉让您有这样的服务体验,我们一定会深刻反省和改进。请问您具体是在哪个时间段拨打的电话?是否有拨打错误的号码?我会立即核实情况并追究服务人员的失职问题。再次向您致以诚挚的歉意,我们会做出改正。,0,2023/10/19 09:20,4
客户4,客服4,就在昨天下午4点多的时候,你们那个电话号码*********。我连打了三四次都没人接。,1,2023/10/19 09:25,4
客户4,客服4,很抱歉让您久等,我核实了下午4点的电话记录,当时确实出现了临时人力紧缺的情况导致了延误接听。这绝对是我们的失误,我们会加大热线人员的配备,杜绝今后出现这种情况。作为补救,如果您需要的话,我可以立即为您开通绿色通道。,0,2023/10/19 09:30,4
客户5,客服5,哈哈你们广告语"性能超神"真是太有喜感了,我都被逗乐了!,1,2023/10/20 14:40,5
客户5,客服5,您真是幽默风趣!那句广告语的确比较搞笑,但我们的产品性能的确超乎您的想象哦。不过话说回来,生活还是需要一点幽默的元素,才不会索然无味对吧?欢迎您继续对我们各种有趣的评论。,0,2023/10/20 14:45,5
客户5,客服5,嗯嗯,期待你们出个带喷火的产品,那就真的超神了!哈哈哈,开个玩笑。,1,2023/10/20 14:50,5
客户5,客服5,哈哈哈您的笑话实在太搞笑了!带喷火的产品我们暂时还真开发不出来,不过我会建议我们的研发部门考虑下,说不定有一天真能推出"超神加持版"呢?感谢您的有趣点评,期待我们的下一个幽默时刻!,0,2023/10/20 14:55,5
客户6,客服6,你好,请问有什么行业术语我需要知道吗?这些专业词汇总是让我一头雾水。,1,2023/10/21 10:30,6
客户6,客服6,不好意思,我们应该避免使用专业的行业术语,用最通俗易懂的语言与客户沟通。如果您在我们交流中遇到任何不明白的地方,欢迎随时询问,我会给予详细解释。,0,2023/10/21 10:35,6
客户7,客服7,您好,请问我可以换一个颜色的商品吗?,1,2023/10/7 13:22,7
客户7,客服7,尊敬的客户,您好!当然可以更换颜色,请问您需要更换成什么颜色的商品呢?我们会尽快为您处理。,0,2023/10/7 13:25,7
客户8,客服8,我最近买的产品有点问题,质量不太好。,1,2023/10/8 09:45,8
客户8,客服8,亲爱的先生/小姐,对于您反映的产品质量问题我表示万分抱歉!我会立即启动退货退款流程,请耐心等待进一步的处理通知。,0,2023/10/8 09:50,8
客户9,客服9,我要退货,1,2023/10/2 11:00,9
客户9,客服9,很抱歉让您有不愉快的购物体验,我们会妥善处理您的退货申请。退货流程很简单,我这就为您详细说明。,0,2023/10/2 11:02,9
客户10,客服10,谢谢您的热情服务!我非常满意。,1,2023/10/10 11:35,10
客户10,客服10,非常感谢您的肯定,我们会一如既往为您提供优质的服务!,0,2023/10/10 11:38,10
客户11,客服11,你们的产品性能有什么提升吗?不如给我详细介绍一下。,1,2023/10/11 14:20,11
客户11,客服11,好的,我们最新产品在性能方面有了非常大的提升!比如处理速度提高了30%,续航时间延长2小时等等,总之会给您带来更优质的体验!,0,2023/10/11 14:25,11
客户12,客服12,不好意思,我等了很久都没人回复,真是太慢了!,1,2023/10/12 17:05,12
客户12,客服12,对不起亲爱的客户,让您久等了,我们一定会加强服务效率,给您及时的回复,再次抱歉!,0,2023/10/12 17:07,12
客户13,客服13,哈哈哈,你们公司的口号"用户至上"真是太有意思了!,1,2023/10/13 10:30,13
客户13,客服13,哈哈您真有幽默感,是的我们公司一直把"用户至上"视为经营理念,欢迎您继续点评!,0,2023/10/13 10:33,13
客户14,客服14,尊敬的客服小姐,不知道您怎么看待最近颇受争议的产品收费新政策?顾客对此意见很大。,1,2023/10/22 15:00,14
客户14,客服14,关于这一新政策,我个人观点是公司应该更多听取用户的反馈意见,在决策时审慎权衡利弊。不过具体情况我也不太了解,如果您有什么其他疑问,欢迎继续询问。,0,2023/10/22 15:05,14
客户15,客服15,亲爱的小姐,谢谢您一直以来的热情服务!我对你们公司的产品和服务态度都非常满意呢。,1,2023/10/23 11:20,15
客户15,客服15,非常感谢您的肯定,这是我们前进的最大动力!我们会一如既往为您提供优质的产品和服务,也欢迎您继续提出任何宝贵意见。,0,2023/10/23 11:25,15
客户16,客服16,我想请问一下,你们有没有针对孩子的相关产品线?比如儿童智能手表之类的。,1,2023/10/24 14:40,16
客户16,客服16,非常抱歉,我们公司目前并没有开发面向儿童的产品线,主要还是一些数码电子消费品。如果您有相关需求,建议可以咨询下其他一些专门的儿童用品品牌哦。,0,2023/10/24 14:45,16
客户17,客服17,你好,请问你们公司最新一款旗舰机型的处理器性能如何?听说算力提升很大,用起来会不会特别快呢?,1,2023/10/25 16:30,17
客户17,客服17,是的,新一代处理器的性能有了非常大的提升,运算能力和多线程处理效率都得到了极大的增强。不论是办公还是娱乐,您都可以体会到流畅无阻碍的超快速度!绝对是前所未有的极致体验哦!,0,2023/10/25 16:35,17
客户18,客服18,不好意思啊,我刚才说话可能有点太生气了。你们公司的服务态度其实还是不错的,我也很满意。,1,2023/10/26 09:15,18
客户18,客服18,亲爱的先生/小姐,非常感谢您的谅解和认可!我们会继续努力为您提供更优质的服务体验。如有任何其他需求,也欢迎您随时提出。,0,2023/10/26 09:20,18
客户19,客服19,你好,不知道你们公司有没有提供上门安装等增值服务?就像其他辅导班那样的上门辅导。,1,2023/10/27 13:55,19
客户19,客服19,非常抱歉,我们公司目前暂时没有提供上门服务等相关业务,主要是销售一些数码产品。您所说的辅导班等服务并不属于我们的范畴,还望您能理解。,0,2023/10/27 14:00,19
客户20,客服20,你好,请教一个小问题,我女儿今年8岁,上小学二年级,最近对编程特别感兴趣,不知道你们那里有没有相应的儿童编程班可以报名呢?,1,2023/10/28 10:10,20
客户20,客服20,非常抱歉,我们公司的业务范围主要集中在销售数码电子产品,暂时并未涉及儿童培训、辅导班等相关领域。不过我也很欣赏您女儿对编程如此着迷,这对培养逻辑思维能力非常有益。如果您有相关需求,建议可以咨询下其他一些专业的培训机构哦。,0,2023/10/28 10:15,20
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


# Print the output text

print(replace_commas_in_message_content(input_text))
