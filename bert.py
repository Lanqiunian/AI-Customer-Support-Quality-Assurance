import pandas as pd
from transformers import BertTokenizer, BertForSequenceClassification
from torch.utils.data import DataLoader, Dataset
import torch

import main
from main import test_0


# 加载停用词和中文分词的函数定义
# ...

class CustomerServiceDataset(Dataset):
    def __init__(self, texts, tokenizer, max_len):
        self.texts = texts
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, item):
        text = str(self.texts[item])
        encoding = self.tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=self.max_len,
            return_token_type_ids=False,
            padding='max_length',
            return_attention_mask=True,
            return_tensors='pt',
            truncation=True
        )

        return {
            'text': text,
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten()
        }

def load_data(dataframe, column_name='消息内容'):
    # 筛选出发送方为0的行
    service_messages = dataframe[dataframe['发送方'] == 0][column_name]
    return service_messages

def create_data_loader(df, tokenizer, max_len, batch_size):
    ds = CustomerServiceDataset(
        texts=df.to_numpy(),
        tokenizer=tokenizer,
        max_len=max_len
    )

    return DataLoader(
        ds,
        batch_size=batch_size
    )

# 参数设置
PRE_TRAINED_MODEL_NAME = 'bert-base-chinese'
MAX_LEN = 128
BATCH_SIZE = 16

# 加载模型和分词器
tokenizer = BertTokenizer.from_pretrained(PRE_TRAINED_MODEL_NAME)
model = BertForSequenceClassification.from_pretrained(PRE_TRAINED_MODEL_NAME)

# 加载数据
texts = main.tokenized

# 创建数据加载器
data_loader = create_data_loader(texts, tokenizer, MAX_LEN, BATCH_SIZE)

# 情感分析函数
def sentiment_analysis(model, data_loader):
    model = model.eval()
    sentiments = []
    with torch.no_grad():
        for d in data_loader:
            input_ids = d["input_ids"]
            attention_mask = d["attention_mask"]
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask
            )
            _, preds = torch.max(outputs.logits, dim=1)
            sentiments.extend(preds.tolist())
    return sentiments

# 执行情感分析
sentiments = sentiment_analysis(model, data_loader)
print(sentiments)
