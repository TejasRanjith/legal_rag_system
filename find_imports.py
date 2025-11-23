try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    print("Found in langchain.text_splitter")
except ImportError:
    print("Not in langchain.text_splitter")

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    print("Found in langchain_text_splitters")
except ImportError:
    print("Not in langchain_text_splitters")

try:
    from langchain.chains import RetrievalQA
    print("Found in langchain.chains")
except ImportError:
    print("Not in langchain.chains")

try:
    from langchain.prompts import PromptTemplate
    print("Found in langchain.prompts")
except ImportError:
    print("Not in langchain.prompts")

try:
    from langchain_core.prompts import PromptTemplate
    print("Found in langchain_core.prompts")
except ImportError:
    print("Not in langchain_core.prompts")
