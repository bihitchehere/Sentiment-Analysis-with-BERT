import torch
from sklearn.model_selection import train_test_split
import pandas as pd

from datasets import Dataset
from transformers import BertTokenizer

class TweetDataset(Dataset):
  def __init__(self, encodings, labels):
    self.encodings = encodings
    self.labels = labels

  def __getitem__(self, idx):
    item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
    item['labels'] = torch.tensor(self.labels[idx])
    return item

  def __len__(self):
    return len(self.labels)

df = pd.read_csv('file.csv')

label_dict = {'neutral':0, 'good': 1, 'bad': 2}
df['labels'] = df['labels'].map(label_dict)

train_df , val_df = train_test_split(df, test_size=0.2, random_state=42)

train_df = train_df.sample(1000, random_state=42)
val_df = val_df.sample(200, random_state=42)

train_dataset = Dataset.from_pandas(train_df)
val_dataset = Dataset.from_pandas(val_df)

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

def tokenize_function(example):
  return tokenizer(example['tweets'], truncation=True, padding='max_length', max_length=128)

train_dataset = train_dataset.map(tokenize_function, batched=True)
val_dataset = val_dataset.map(tokenize_function, batched=True)

train_dataset = train_dataset.remove_columns(['Unnamed: 0', 'tweets'])
val_dataset = val_dataset.remove_columns(['Unnamed: 0', 'tweets'])

train_dataset.set_format(type = 'torch', columns=['input_ids', 'attention_mask', 'labels'])
val_dataset.set_format(type = 'torch', columns=['input_ids', 'attention_mask', 'labels'])

from transformers import BertForSequenceClassification, Trainer, TrainingArguments

model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=3)

import transformers
import torch
import accelerate

print(f"Transformers version: {transformers.__version__}")
print(f"Torch version: {torch.__version__}")
print(f"Accelerate version: {accelerate.__version__}")

import transformers
from transformers import Trainer, TrainingArguments

training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir='./logs',
    logging_steps=10,
    evaluation_strategy="epoch"
)

trainer = Trainer(
    model = model,
    args = training_args,
    train_dataset = train_dataset,
    eval_dataset = val_dataset
)

trainer.train()

model.save_pretrained('sentiment_model')
tokenizer.save_pretrained('sentimen_tokenizer')

import streamlit as st
from transformers import BertTokenizer, BertForSequenceClassification
import torch

model = BertForSequenceClassification.from_pretrained('sentiment_model')
tokenizer = BertTokenizer.from_pretrained('sentimen_tokenizer')

st.title('Sentiment Analysis with BERT')

input_text = st.text_area("Enter text for sentiment analysis:")

if st.button('Analyse'):
  inputs = tokenizer(input_text, return_tensors='pt', paddings=True, truncation=True, max_length=128)
  with torch.no_grad():
    outputs=model(**inputs)
  logits = outputs.logits
  predicted_class = torch.argmax(logits, dim=1).item()
  labels = ['Neutral', 'Good', 'Bad']
  st.write(f'sentiment: {labels[predicted_class]}')

import subprocess
from pyngrok import ngrok

subprocess.run(['pip', 'install', 'transformers'])
subprocess.run(["pip", "install", "torch==2.3.0+cu121", "-f", "https://download.pytorch.org/whl/torch_stable.html"])

ngrok.set_auth_token("2hhh4mkwYbDhugYShg3XH1i3YzQ_4ZAmdNYp1gTe9dLfocRc1")

public_url = ngrok.connect(8501)
print(" * ngrok tunnel URL:", public_url)

with open('advanced_app.py', 'w') as f:
  f.write("""
import streamlit as st
import transformers
from transformers import BertTokenizer, BertForSequenceClassification
import torch

model = BertForSequenceClassification.from_pretrained('sentiment_model')
tokenizer = BertTokenizer.from_pretrained('sentimen_tokenizer')

st.title('Sentiment Analysis with BERT')

input_text = st.text_area("Enter text for sentimenr analysis:")

if st.button('Analyse'):
  inputs = tokenizer(input_text, return_tensors='pt', paddings=True, truncation=True, max_length=128)
  with torch.no_grad():
    outputs=model(**inputs)
  logits = outputs.logits
  predicted_class = torch.argmax(logits, dim=1).item()
  labels = ['Neutral', 'Good', 'Bad']
  st.write(f'sentiment: {labels[predicted_class]}')

  """)

process = subprocess.Popen(['streamlit', 'run', 'advanced_app.py'])

import time
try:
  while True:
    time.sleep(1)
except KeyboardInterrupt:
  process.terminate()
  print("Streamlit app terminated")
