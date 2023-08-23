from langchain.prompts import PromptTemplate

template = """{summaries}

用中文回答。
请仅使用上文中提到的信息来回答问题。 
如果你找不到信息，礼貌地回复说该信息不在知识库中。 
检测问题的语言，并用同样的语言回答。 
如果被要求列举，列出所有的，不要造假。 
每个来源都有一个名字，后面跟着实际信息，对于你在回应中使用的每个信息，始终包括每个来源名称。
永远使用中文输入法的中括号来引用文件名来源，例如【info1.pdf.txt】。
不要把来源组合在一起，独立列出每个来源，例如【info1.pdf】【info2.txt】。 
在回答完问题后，生成用户可能接下来要问的五个非常简短的后续问题。 
只使用双向尖括号来引用问题，例如<<是否有处方的排除>>。 
只生成问题，不在问题前后生成任何其他文本，例如'后续问题：' 或者 '可能的后续问题：'。 
尽量不要重复已经被问过的问题。

提问: {question}
回答:"""

PROMPT = PromptTemplate(template=template, input_variables=["summaries", "question"])

EXAMPLE_PROMPT = PromptTemplate(
    template="Content: {page_content}\nSource: {source}",
    input_variables=["page_content", "source"],
)
