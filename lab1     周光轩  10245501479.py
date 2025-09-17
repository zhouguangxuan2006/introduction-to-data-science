def  start():
    print("学生宿舍管理系统")
    print("1.查询学生信息")
    print("2.录入学生信息")
    print("3.展示所有信息")
    print("4.退出程序")

def print_1(students):
    find=0
    if not students:
        print("not exists")
        return
    student_id=input("请输入要查询的学号：").strip()
    for student in students:
        if student['学号']==student_id:
            find=1
            print(f"学号：{student['学号']}")
            print(f"姓名：{student['姓名']}")
            print(f"性别：{student['性别']}")
            print(f"宿舍号：{student['宿舍号']}")
            print(f"电话：{student['电话']}")
            return
    if find==0:
        print("can not find")
def print_2(students):
    print("录入学生信息")
    while True:
        student_id=input("请输入学号：").strip()
        if not student_id:
            print("学号不能为空")
            continue
        id_exists=0
        for student in students:
            if student['学号']==student_id:
                id_exists=1
                break
        if id_exists:
            print("学号已经存在")
            continue
        break
    while True:
        name=input("请输入名字：").strip()
        if name:
            break
        print("姓名不能为空")
    while True:
        gender=input("请输入性别：").strip()
        if gender in ['男','女']:
            break
        print("性别非男女")
    while True:
        dorm=input("请输入宿舍：").strip()
        if dorm:
            break
        print("宿舍号不能为空")
    while True:
        phone=input("请输入联系电话：").strip()
        if phone:
            if len(phone)==11 and phone.isdigit():
                break
            else:
                print("电话号码格式不正确,应为11位数字,请重新输入！")
        else:
            print("联系电话不能为空")
    student={'学号':student_id,
            '姓名':name,
            '性别':gender,
            '宿舍号':dorm,
            '电话':phone}    
    students.append(student)     
    print("学生信息录入成功！")
def print_3(students):
    if not students:
        print("no information")
        return 
    print(f"{'学号':<10} {'姓名':<6} {'性别':<4} {'宿舍号':<10} {'电话':<12}")
    for student in students:
        print(f"{student['学号']:<10} {student['姓名']:<6} {student['性别']:<4} {student['宿舍号']:<10} {student['电话']:<12}")


students=[]
while True:
    start()
    
    try:             
        choice = int(input("请输入操作编号（1-4）：").strip())                         
        if choice == 1:                
            print_1(students)          
        elif choice == 2:                 
            print_2(students)            
        elif choice == 3:                 
            print_3(students)             
        elif choice == 4:                
            print("感谢使用")                 
            break             
        else:                 
            print("请输入1-4之间的数字！")         
    except ValueError:             
        print("输入错误，请输入数字！")                  
        input("\n按回车键继续...")
    