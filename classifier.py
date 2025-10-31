# %%
import pandas as pd
import langchain
import os
import time

from langchain.chat_models import ChatOllama

from langchain.output_parsers import PydanticOutputParser
from langchain_core.output_parsers import BaseOutputParser
from langchain.prompts import ChatPromptTemplate

from prompts import system_prompt, user_prompt


# %%
df = pd.read_csv("prswithtasks.csv")

df.head()

# %%
class PerformanceClassifierParser(BaseOutputParser):
    """
    Parses the output of an LLM call to classify a pull request.
    The expected output is 'runtime', 'energy',.
    """

    def parse(self, text: str) -> str:
        """
        Parses the text output from the language model.

        Args:
            text: The text output from the language model.

        Returns:
            The parsed classification ('runtime', 'energy'').
        """
        cleaned_text = text.strip().lower()
        if cleaned_text in ["runtime", "energy"]:
            return cleaned_text
    

    def get_format_instructions(self) -> str:
        """Instructions on how the LLM should format its response."""
        return "Your output should be one of: 'runtime', or 'energy'. It should not be None!"

parser = PerformanceClassifierParser()
print(parser.get_format_instructions())

# %%
model_name = 'qwen3:14b'
llm = ChatOllama(model=model_name)

# %%
classification_prompt_template = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("user", user_prompt),
])

parser = PerformanceClassifierParser()

# %%
print(parser.get_format_instructions())

# %%
chain = classification_prompt_template | llm | parser

# %%
classified_df = df.copy()

# %%
for idx, row in classified_df.iterrows():
    title = row['title']
    body = row['body']

    input_vars = {
        "format_instructions": parser.get_format_instructions(),
        "title": title,
        "body": body,
    }
    
    classification = chain.invoke(input_vars)
    classified_df.at[idx, "classification"] = classification
    
    print(f"Classification: {classification}")

# %%
classified_df.to_csv("classified_prs.csv")

# %%
classification_counts = classified_df['classification'].value_counts(dropna=False)
print(classification_counts)


