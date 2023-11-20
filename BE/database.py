from pymongo import MongoClient

class DB:
    def __init__(self, username, password, cluster_name, database_name):
        self.username = username
        self.password = password
        self.cluster_name = cluster_name
        self.database_name = database_name
        self.client = MongoClient(f"mongodb+srv://{username}:{password}@{cluster_name}.mongodb.net/{database_name}?retryWrites=true&w=majority")

        self.db = self.client[database_name]
        self.collection = self.db["research"]
        self.collection.create_index([("query", "text")])

    @staticmethod   
    def get_instance():
        return DB("trongnt2002", "trongnt2002", "admin.4xteipz", "crawler")



# # Kết nối đến MongoDB Atlas
# # client = MongoClient(f"mongodb+srv://{username}:{password}@{cluster_name}.mongodb.net/{database_name}?retryWrites=true&w=majority")

# # # Chọn cơ sở dữ liệu
# # db = client[database_name]


# # Kết nối đến MongoDB
# # client = MongoClient("mongodb+srv://trongnt2002:trongnt2002@admin.4xteipz.mongodb.net/")  # Thay đổi URL kết nối nếu cần
# # db = client["google_scholar_db"]
# # collection = db["research"]

# # collection = db["your_collection_name"]
# # data = {"name": "Object detection", "age": 25, "city": "New York"}
# # collection.insert_one(data)

# collection = DB.get_instance().collection
# input_word = "Object"
# regex_pattern = re.compile(f".*{input_word}.*", re.IGNORECASE)
# print(regex_pattern)
# # Tìm kiếm trong cơ sở dữ liệu
# result = collection.find_one({"name": regex_pattern})

# # Kiểm tra kết quả
# if result:
#     print(f"Từ '{input_word}' tồn tại trong cơ sở dữ liệu.")
# else:
#     print(f"Từ '{input_word}' không tồn tại trong cơ sở dữ liệu.")




# # Lấy danh sách các bản ghi từ bảng
# # records = collection.find()
# # for record in records:
# #     print(record)

