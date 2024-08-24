# from langchain_google_alloydb_pg import AlloyDBEngine, AlloyDBVectorStore
# from langchain_google_vertexai import VertexAIEmbeddings
# import os
# from langchain_community.document_loaders import PyPDFLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter

# from ask_chuck_api.rag.constants import *


# current_dir = os.path.dirname(os.path.abspath(__file__))
# file_path = os.path.join(current_dir, "Charles-Owen",
#                          "Bottom-up-top-down-updown09.pdf")

# loader = PyPDFLoader(
#     "https://firebasestorage.googleapis.com/v0/b/askchuck.appspot.com/o/Charles%20Owen%2FBottom-up-top-down-updown09.pdf?alt=media&token=c6bd765b-593a-44b2-b389-de64fd8e95ee",
#     extract_images=True
# )

# docs = loader.load()

# print(docs)

# text_splitter = RecursiveCharacterTextSplitter(
#     chunk_size=1000, chunk_overlap=500

# )
# chunks = text_splitter.split_documents(docs)

# chunk = chunks[0]

# print(chunks)


# engine = AlloyDBEngine.from_instance(
#     project_id=PROJECT_ID,
#     region=REGION,
#     cluster=CLUSTER,
#     instance=INSTANCE,
#     database=DATABASE,
#     user=DATABASE_USER,
#     password=DATABASE_PASSWORD,
# )

# # engine.init_vectorstore_table(
# #     table_name=TABLE_NAME,
# #     # Vector size for VertexAI model(textembedding-gecko@latest)
# #     vector_size=768,
# # )

# embedding = VertexAIEmbeddings(
#     model_name="textembedding-gecko@latest", project=PROJECT_ID
# )

# store = AlloyDBVectorStore.create_sync(
#     engine=engine,
#     table_name=TABLE_NAME,
#     embedding_service=embedding,
# )

# # store.add_documents(chunks)
