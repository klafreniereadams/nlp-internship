# abstractive_summarization.py

# Suggested by copilot.

"""
(Optional Future Work)
 For abstractive summarization: a fine-tuned T-5 model
 trained on real estate listing remarks and human-created summaries.
-------------------------------------------------------------------
 This is a skeleton outline of the steps required to
 fine-tune a T-5-small model for our purposes.

Outline:

- Dataset preparation
- Tokenization
- PyTorch dataset wrapper
- T5-small loading
- CPU-friendly training configuration
- HuggingFace Trainer setup
- Fine-tuning loop
- Inference function

This is a loose roadmap for future integration of a fine-tuned
t-5-small model that could generate summaries of listings.
It's future work for a final product.
"""

from transformers import T5Tokenizer, T5ForConditionalGeneration
from transformers import Trainer, TrainingArguments
from torch.utils.data import Dataset
import pandas as pd
import torch

# ----------------------------------------------------------
# Load and Prepare Dataset
# ----------------------------------------------------------
def load_dataset(csv_path):
    df = pd.read_csv(csv_path)

    # Create input/target pairs
    # input_text: "summarize: <remarks>"
    # target_text: "<desired summary>"
    # (target summaries may initially come from extractive model)
    data = []
    for _, row in df.iterrows():
        input_text = "summarize: " + str(row["L_Remarks"])
        target_text = str(row["summary"])  # placeholder field
        data.append({"input_text": input_text, "target_text": target_text})

    return data

# ----------------------------------------------------------
# Tokenization + Dataset Class
# ----------------------------------------------------------
class T5SummaryDataset(Dataset):
    def __init__(self, data, tokenizer, max_input_len=256, max_target_len=64):
        self.data = data
        self.tokenizer = tokenizer
        self.max_input_len = max_input_len
        self.max_target_len = max_target_len

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]

        input_enc = self.tokenizer(
            item["input_text"],
            max_length=self.max_input_len,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )

        target_enc = self.tokenizer(
            item["target_text"],
            max_length=self.max_target_len,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )

        return {
            "input_ids": input_enc.input_ids.squeeze(),
            "attention_mask": input_enc.attention_mask.squeeze(),
            "labels": target_enc.input_ids.squeeze()
        }


# ----------------------------------------------------------
# Load Model + Tokenizer
# ----------------------------------------------------------
def load_model():
    tokenizer = T5Tokenizer.from_pretrained("t5-small")
    model = T5ForConditionalGeneration.from_pretrained("t5-small")
    return tokenizer, model

# ----------------------------------------------------------
# Training definition
# ----------------------------------------------------------
def get_training_args(output_dir="t5_small_finetuned"):
    return TrainingArguments(
        output_dir=output_dir,
        evaluation_strategy="epoch",
        learning_rate=2e-4,
        per_device_train_batch_size=1,     # CPU-friendly
        gradient_accumulation_steps=8,     # batch size might need to be smaller
        num_train_epochs=3,
        weight_decay=0.01,
        save_total_limit=2,
        logging_steps=50
    )
# look up recommendations for fine-tuning a T-5 using a CPU.
# look into GPU usage for fine-tuning

# ----------------------------------------------------------
# Trainer Setup
# ----------------------------------------------------------
def build_trainer(model, tokenizer, train_dataset, val_dataset, training_args):
    def compute_metrics(eval_pred):
        # ROUGE-L evaluation would go here
        return {"rougeL": 0.0}

    return Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics
    )

# ----------------------------------------------------------
# Fine-Tuning Loop
# ----------------------------------------------------------
def train_model():
    # Placeholder paths
    train_data = load_dataset("train.csv")
    val_data = load_dataset("val.csv")

    tokenizer, model = load_model()

    train_dataset = T5SummaryDataset(train_data, tokenizer)
    val_dataset = T5SummaryDataset(val_data, tokenizer)

    training_args = get_training_args()
    trainer = build_trainer(model, tokenizer, train_dataset, val_dataset, training_args)

    trainer.train()
    trainer.evaluate()
    trainer.save_model()


# ----------------------------------------------------------
# Inference Pipeline
# ----------------------------------------------------------
def generate_summary(model, tokenizer, remarks):
    input_text = "summarize: " + remarks

    enc = tokenizer.encode(input_text, return_tensors="pt", truncation=True)
    output = model.generate(enc, max_length=128)

    return tokenizer.decode(output[0], skip_special_tokens=True)
