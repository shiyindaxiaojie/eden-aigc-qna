from langchain.prompts import PromptTemplate

prompt = PromptTemplate(
    input_variables=["product"],
    template="哪些公司生产{product}?",
)

print(prompt.format(product="iphone"))
