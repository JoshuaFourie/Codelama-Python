# finetune_model.py
from transformers import Trainer, TrainingArguments, AutoModelForCausalLM, AutoTokenizer
import os
import glob
import json

# Model and data paths
model_name = "meta-llama/CodeLlama-13b-Instruct-hf"
training_data_dir = "./training_data"  # Directory containing your JSON files
output_dir = "./finetuned-model"

# Find all JSON files in the directory
json_files = glob.glob(os.path.join(training_data_dir, "*.json"))
print(f"Found {len(json_files)} JSON files in {training_data_dir}")

# Combine all JSON files into a single JSONL file for training
temp_jsonl_file = os.path.join(training_data_dir, "combined_training_data.jsonl")

with open(temp_jsonl_file, "w", encoding="utf-8") as outfile:
    for json_file in json_files:
        try:
            with open(json_file, "r", encoding="utf-8") as infile:
                data = json.load(infile)
                
                # Process the data based on your JSON structure
                # Example: Convert comparison data to training format
                if "source" in data and data["source"] == "AI_Comparison":
                    # Choose which response to use (other_ai_response is often better)
                    # You might want to implement logic to decide which response to use
                    training_example = {
                        "messages": [
                            {"role": "user", "content": data["instruction"]},
                            {"role": "assistant", "content": data["other_ai_response"]}
                        ]
                    }
                else:
                    # Regular training examples
                    training_example = {
                        "messages": [
                            {"role": "user", "content": data["instruction"]},
                            {"role": "assistant", "content": data["response"]}
                        ]
                    }
                
                # Write as JSONL (one JSON object per line)
                outfile.write(json.dumps(training_example) + "\n")
                print(f"Processed: {json_file}")
        except Exception as e:
            print(f"Error processing {json_file}: {e}")

# Load model and tokenizer
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Define training arguments
training_args = TrainingArguments(
    output_dir=output_dir,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    num_train_epochs=3,
    learning_rate=2e-5,
    save_strategy="epoch",
    logging_dir="./logs",
    logging_steps=10,
    fp16=True,
    save_total_limit=2,
)

# Load the combined JSONL dataset
from datasets import load_dataset
train_dataset = load_dataset("json", data_files=temp_jsonl_file)["train"]
print(f"Dataset loaded with {len(train_dataset)} examples")

# Tokenize the dataset
def tokenize_function(examples):
    # This processes the messages format from the JSONL file
    prompts = []
    for message_list in examples["messages"]:
        # Create prompt format: "user: ... assistant: ..."
        formatted_text = ""
        for message in message_list:
            role = message["role"]
            content = message["content"]
            formatted_text += f"{role}: {content}\n"
        prompts.append(formatted_text)
    
    return tokenizer(prompts, truncation=True, padding="max_length", max_length=1024)

# Apply tokenization
tokenized_dataset = train_dataset.map(tokenize_function, batched=True)

# Initialize the Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    tokenizer=tokenizer,
)

# Start training
trainer.train()

# Save the final model
model.save_pretrained(output_dir)
tokenizer.save_pretrained(output_dir)

# Optionally, clean up the temporary JSONL file
# os.remove(temp_jsonl_file)