import sqlite3

class SQLite3:
    def __init__(self):
        self.path = input("请输入数据库的路径:")
        self.conn = sqlite3.connect(self.path)
        self.cur = self.conn.cursor()

    #创建数据表
    def Create(self,table):

        #指令提示词
        field_dict = {"I":"INTEGER","T":"TEXT","R":"REAL","B":"BLOB",
                      "P":"PRIMARY KEY","N":"NOT NULL","PN":"PRIMARY KEY NOT NULL"}
        ts_str = ("类型提示：INTEGER类型输入I,TEXT类型输入T,REAL类型输入R,BLOB类型输入B\n"
                  "约束提示：没有约束回车,PRIMARY KEY输入P,NOT NULL输入N (如果有两个约束如"
                  "PRIMARY KEY NOT NULL 就输入PN,两个约束的开头)")

        #输入字段
        field_num = int(input("请输入你想创建的字段数量："))
        field_list = []
        input_str = ""
        for _ in range(field_num):
            print(ts_str)
            field_list.append([input("字段名称:"),input("字段类型："),input("约束类型：")])
            print()
        for _ in field_list:
            _[1] = field_dict.get(_[1],"")
        for _ in field_list:
            _[2] = field_dict.get(_[2], "")
        for index , _ in enumerate(field_list):
            if index != len(field_list) - 1:
                input_str += _[0] + " " + _[1] + " " + _[2] + ","
            else:
                input_str += _[0] + " " + _[1] + " " + _[2]

        C_str = f"CREATE TABLE {table} ({input_str});"
        #执行指令并提交
        self.cur.execute(C_str)
        self.conn.commit()

    #SQLite 查询指令
    def Select(self,table):

        is_WHERE = False
        where_str = ""
        field_select_str = []
        table_field = []

        table_okay = self.cur.execute(f"PRAGMA table_info({table});") #用来获取表的标题列
        for f in table_okay:
            table_field.append(f[1])

        #用来与用户交互输入字段
        for i in table_field:
            print(f"字段: {i}")
            input_char = input("请确认要显示的字段(输入1选择,如果输入*表示全选,否则不选)：")
            if  input_char == "1":
                field_select_str.append(i)
            elif input_char == "*":
                field_select_str = "*"
                break

        #用来与用户交互输入WHERE表达式
        input_char = input("是否加入WHERE过滤筛选(输入1选是)：")
        if input_char == "1":
            is_WHERE = True
            expression = []
            num = int(input("请输入表达式的数量(一定是正整数)："))

            for i in range(num):
                print(table_field)
                expression.append(input("请输入表达式(形如 字段1 < 数量)："))
                if i != num - 1:
                    expression.append(input("请输入连接(and 或者 or)：").upper())

            where_str = " ".join(expression)

        #用来判断是否要显示全部字段
        if len(field_select_str) == len(table_field) or field_select_str == '*':
            field_select_str = "*"
        else:
            field_select_str = ','.join(field_select_str)

        #判断SELECT语句中是否有WHERE表达式,并执行
        if is_WHERE:
            execute_str = f"SELECT {field_select_str} FROM {table} WHERE {where_str};"
            show_info = self.cur.execute(execute_str)
        else:
            execute_str = f"SELECT {field_select_str} FROM {table};"
            show_info = self.cur.execute(execute_str)

        #用来显示结果
        for _ in show_info:
            print(_)

    #SQLite 更新数据指令
    def Update(self,table):

        is_WHERE = False
        table_field = []
        confirm_field = []
        confirm_field_dict = {}
        value = []
        field_value = []
        where_str = ""

        table_okay = self.cur.execute(f"PRAGMA table_info({table});") #用来获取表的标题列
        for f in table_okay:
            table_field.append(f[1])

        #用来确认要修改的字段
        for f in table_okay:
            print(f"字段: {f[1]}")
            input_char = input("请确认要修改的字段(输入1选择,否则不选)：")
            if  input_char == "1":
                confirm_field_dict[f[1]] = f[2]

        #用来填写修改字段的值
        if not confirm_field_dict:
            print("没有要修改的字段")
            return
        else:
            for k in confirm_field_dict.keys():
                input_str = input(f"字段：{k} 类型：{confirm_field_dict[k]} 请确认要修改的字段的值:")
                confirm_field.append(k)
                match confirm_field_dict[k]:
                    case "INTEGER":
                        value.append(int(input_str))
                    case "TEXT":
                        value.append(f"@{input_str}@")
                    case "REAL":
                        value.append(float(input_str))
                    case "BLOB":
                        value.append(int(input_str))

            #用来与用户交互输入WHERE表达式
            input_char = input("是否加入WHERE过滤筛选(输入1选是)：")
            if input_char == "1":
                is_WHERE = True
                expression = []
                num = int(input("请输入表达式的数量(一定是正整数)："))

                for i in range(num):
                    print(table_field)
                    expression.append(input("请输入表达式(形如 字段1 < 数量)："))
                    if i != num - 1:
                        expression.append(input("请输入连接(and 或者 or)：").upper())
                where_str = " ".join(expression)

                #组合执行语句
                for i in range(len(confirm_field)):
                    field_value.append(f"{confirm_field[i]} = {value[i]}")
                field_value = ','.join(field_value)
                field_value = field_value.replace("@","'")

        #判断SELECT语句中是否有WHERE表达式,并执行提交
        if is_WHERE:
            execute_str = f"UPDATE {table} SET {field_value} WHERE {where_str};"
        else:
            execute_str = f"UPDATE {table} SET {field_value};"

        self.cur.execute(execute_str)
        self.conn.commit()

    #SQLite 删除指令
    def Delete(self,table):

        is_WHERE = False
        where_str = ""
        table_field = []

        table_okay = self.cur.execute(f"PRAGMA table_info({table});") #用来获取表的标题列
        for f in table_okay:
            table_field.append(f[1])

        #用来与用户交互输入WHERE表达式
        input_char = input("是否加入WHERE过滤筛选(输入1选是)：")
        if input_char == "1":
            is_WHERE = True
            expression = []
            num = int(input("请输入表达式的数量(一定是正整数)："))

            for i in range(num):
                print(table_field)
                expression.append(input("请输入表达式(形如 字段1 < 数量)："))
                if i != num - 1:
                    expression.append(input("请输入连接(and 或者 or)：").upper())
            where_str = " ".join(expression)

        #判断SELECT语句中是否有WHERE表达式,并执行提交
        if not is_WHERE:
            execute_str = f"DELETE FROM {table};"
        else:
            execute_str = f"DELETE FROM {table} WHERE {where_str};"

        self.cur.execute(execute_str)
        self.conn.commit()

    #SQLite 插入指令
    def Insert(self,table):

        table_field_name = []
        Value_str = []
        table_field = self.cur.execute(f"PRAGMA table_info({table});") #用来获取表的标题列
        print("请根据提示,填写数据")

        #依次输入插入记录字段的值
        for i in table_field:
            table_field_name.append(i[1])
            try:
                match i[2].lower():
                    case "integer":
                        Value_str.append(int(input(f"字段:{i[1]}类型:{i[2]}：")))
                    case "real":
                        Value_str.append(float(input(f"字段:{i[1]}类型:{i[2]}：")))
                    case "text":
                        Value_str.append(str(input(f"字段:{i[1]}类型:{i[2]}：")))
                    case "blob":
                        Value_str.append(bool(input(f"字段:{i[1]}类型:{i[2]}：")))
                    case "null":
                        Value_str.append(None)
            except Exception:
                print("录入错误,此次结果不会报错")
                break

        #用来组合语句，并执行提交
        try:
            table_field_name = ",".join(table_field_name)
            value_str = ",".join(['?'] * len(table_field_name))
            insert_execute_str = f"INSERT INTO {table} ({table_field_name}) VALUES({value_str};)"
            self.cur.execute(insert_execute_str, Value_str)
            self.conn.commit()
        except sqlite3.IntegrityError:
            print(f"{table_field_name[0]}重复了,请重新录入")
        else:
            print("录入成功！")

    #用来显示数据表现在的状态
    def Show_info(self,table):
        row = self.cur.execute(f"SELECT * FROM {table};")
        for r in row:
            print(r)
    #用来回滚数据
    def Rollback(self):
        self.conn.rollback()
