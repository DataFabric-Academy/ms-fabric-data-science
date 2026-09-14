# แบบฝึกหัด 0: สร้าง workspace และเตรียมข้อมูล FreshMart

- ประมาณ **30–40** นาที

ในแบบฝึกหัดนี้ คุณจะเรียนรู้วิธี:

- สร้าง Azure Machine Learning workspace
- สร้าง compute instance สำหรับรัน notebook
- สร้าง **Data asset** จากไฟล์ FreshMart แล้วเขียนชั้น Bronze

อ้างอิง: [Tutorial: Create resources you need to get started](https://learn.microsoft.com/azure/machine-learning/quickstart-create-resources) · [Create data assets](https://learn.microsoft.com/azure/machine-learning/how-to-create-data-assets)

> นี่คือทางเลือกฉุกเฉินเมื่อ Fabric Capacity ใช้ไม่ได้ — อย่าแก้ไฟล์ใน `labs/`

## สิ่งที่ต้องมีก่อนเริ่ม

- Azure subscription ที่สร้าง Azure Machine Learning ได้
- บทบาท **Contributor** หรือ **Owner** บน resource group เป้าหมาย
- ถ้ายังไม่มีบัญชี ดู [สร้างบัญชี Azure](https://azure.microsoft.com/pricing/purchase-options/azure-account)

## งานที่ 1: สร้าง workspace

1. ลงชื่อเข้าใช้ [Azure Machine Learning studio](https://ml.azure.com)
2. เลือก **Create workspace**
3. กรอกค่าตามตาราง แล้วเลือก **Create**

| ช่อง | ค่าที่ใส่ |
| :--- | :--- |
| **Workspace name** | `aml-freshmart` หรือ `aml-freshmart-<ชื่อย่อ>` |
| **Subscription** | subscription ที่ได้รับสิทธิ์ |
| **Resource group** | สร้างใหม่ `rg-freshmart-labs` หรือใช้ที่ผู้สอนกำหนด |
| **Region** | ภูมิภาคใกล้ผู้เรียน เช่น `Southeast Asia` |

4. รอจน studio เปิด workspace ได้

**เมื่องานนี้เสร็จ คุณควรเห็น:** เมนูซ้ายมี **Notebooks**, **Automated ML**, **Jobs**, **Models**, **Data**, **Compute**

ถ้าผู้สอนสร้าง workspace ร่วมไว้แล้ว ให้ข้ามงานนี้ แล้วไปงานที่ 2

## งานที่ 2: สร้าง compute instance

1. มุมขวาบน เลือก **New** แล้วเลือก **Compute instance**
2. กรอกค่าตามตาราง
3. เลือก **Review + Create** แล้วเลือก **Create**
4. รอสถานะเป็น **Running**

| ช่อง | ค่าที่ใส่ |
| :--- | :--- |
| **Compute name** | `ci-<ชื่อย่อ>` (ห้ามซ้ำใน workspace) |
| **Virtual machine size** | **Standard_DS11_v2** (CPU) |
| Idle shutdown (ถ้ามี) | **15–30** นาที |

**เมื่องานนี้เสร็จ คุณควรเห็น:** รายการ **Compute instances** แสดงเครื่องของคุณสถานะ **Running**

อ้างอิง: [Create a compute instance](https://learn.microsoft.com/azure/machine-learning/how-to-create-compute-instance)

## งานที่ 3: นำไฟล์แล็บเข้า compute instance

เลือกอย่างใดอย่างหนึ่ง

### ตัวเลือก A — clone repository (แนะนำ)

1. ซ้ายมือเลือก **Notebooks** แล้วเปิดแท็บ **Files**
2. เปิด **Terminal** ของ compute instance
3. รันคำสั่ง:

```bash
cd ~/cloudfiles/code/Users
git clone https://github.com/DataFabric-Academy/ms-fabric-data-science.git
```

โน้ตบุ๊กอยู่ที่ `ms-fabric-data-science/labs-azureml/notebooks/`  
CSV อยู่ที่ `ms-fabric-data-science/labs/data/` — อย่าแก้โฟลเดอร์ `labs/`

### ตัวเลือก B — อัปโหลดจากเครื่อง

1. ใน **Notebooks** สร้างโฟลเดอร์ `freshmart/data/raw/`
2. อัปโหลดสามไฟล์จาก `labs/data/` บนเครื่องคุณ:

| ไฟล์ | ความหมาย |
| :--- | :--- |
| `freshmart_transactions.csv` | ธุรกรรม 3,000 แถว |
| `freshmart_customers.csv` | สมาชิก 1,500 แถว |
| `freshmart_scoring_batch.csv` | ชุดทำนาย 200 แถว |

3. อัปโหลดโน้ตบุ๊กจาก `labs-azureml/notebooks/` ไว้ที่โฟลเดอร์ `freshmart/`

**เมื่องานนี้เสร็จ คุณควรเห็น:** เปิด `00-environment-verification.ipynb` ได้ และมีไฟล์ CSV ครบสามชื่อ

## งานที่ 4: สร้าง Data asset จากหน้า Data

Data asset คือรายการใน workspace ที่ชี้ไปไฟล์ใน datastore — ใช้ซ้ำได้จาก notebook, Automated ML และ Jobs โดยไม่ต้องจำ path

1. ซ้ายมือเลือก **Data**
2. เลือก **Create** > **Data asset**
3. สร้างทีละรายการตามตาราง — ประเภทเป็น **Tabular** ทุกครั้ง
4. แหล่งข้อมูลเลือก **From local files**
5. Datastore เลือก **workspaceblobstore**
6. อัปโหลดไฟล์ CSV จาก `labs/data/` บนเครื่องคุณ (หรือจากโฟลเดอร์ที่ clone มา)
7. **File format** = Delimited, **Delimiter** = Comma, **Column headers** = All files have same headers
8. ตรวจ schema แล้วเลือก **Create**

| Data asset name | ไฟล์ | จำนวนแถวที่ควรเห็นตอนพรีวิว |
| :--- | :--- | :--- |
| `bronze-transactions` | `freshmart_transactions.csv` | ประมาณ 3,000 |
| `bronze-customers` | `freshmart_customers.csv` | ประมาณ 1,500 |
| `scoring-batch` | `freshmart_scoring_batch.csv` | 200 และ**ไม่มี**คอลัมน์ `Churn` |

**เมื่องานนี้เสร็จ คุณควรเห็น:** หน้า **Data** มีสามชื่อด้านบน กดเข้าไปแล้วแท็บ **Preview** แสดงตารางได้

อ้างอิง: [Tutorial: Upload, access, and explore your data](https://learn.microsoft.com/azure/machine-learning/tutorial-explore-data)

## งานที่ 5: รัน notebook ยืนยันสภาพแวดล้อม

1. เปิด `00-environment-verification.ipynb`
2. เลือก compute instance ของคุณ และเคอร์เนล **Python 3.10 - SDK v2**
3. รันทุกเซลล์ตามลำดับ — เซลล์ท้ายจะลงทะเบียน Data asset อีกครั้งถ้ายังไม่มี

**เมื่องานนี้เสร็จ คุณควรเห็น**

- `bronze/transactions` ประมาณ **3,000** แถว
- `bronze/customers` ประมาณ **1,500** แถว
- ข้อความ `Registered data asset` สำหรับ `bronze-transactions` / `bronze-customers` / `scoring-batch`
- ข้อความ `Lab 0 verification passed`

ชั้น Medallion ในแทร็กนี้มีทั้งโฟลเดอร์ไฟล์และ Data asset:

| ชั้น | Data asset | ที่อยู่ไฟล์ | ใช้ในแบบฝึกหัด |
| :--- | :--- | :--- | :--- |
| Bronze | `bronze-transactions`, `bronze-customers` | `data/bronze/` | 0–1 |
| ชุดทำนาย | `scoring-batch` | `labs/data/` หรือ datastore | 0, 4 |
| Silver | `silver-customer-features` | `data/silver/` | 2–3 |
| Gold | `gold-freshmart-predictions` | `data/gold/` | 4 |

## งานที่ 6: ตรวจอินไซต์แรก

ในเซลล์ใหม่ของ notebook รัน:

```python
waste = df_tx.groupby("Category")["WasteCost"].sum().sort_values(ascending=False)
print(waste)
```

**เมื่องานนี้เสร็จ คุณควรเห็น:** หมวด **Bakery** ของเสียสูงสุด (ประมาณ 8,043) ตามด้วย Produce

## ผ่านแบบฝึกหัดเมื่อ

- [ ] เปิด studio ของ workspace ได้
- [ ] compute instance ของตนเองสถานะ **Running**
- [ ] หน้า **Data** มี `bronze-transactions`, `bronze-customers`, `scoring-batch`
- [ ] `Lab 0 verification passed`
- [ ] Bakery เป็นหมวดของเสียสูงสุด

## แก้ปัญหาบ่อย

| อาการ | สิ่งที่ทำต่อ |
| :--- | :--- |
| สร้าง workspace ไม่ได้ | ตรวจสิทธิ์ Contributor/Owner และโควตาในภูมิภาคนั้น |
| สร้าง compute instance ไม่ได้ | เปลี่ยนขนาดเครื่อง หรือขอโควตา CPU |
| ไม่เจอไฟล์ CSV | ใช้ตัวเลือก A หรืออัปโหลดจาก `labs/data/` |
| สร้าง Data asset ไม่ได้ | ตรวจว่าเลือกประเภท **Tabular** และ datastore เป็น **workspaceblobstore** |
| เคอร์เนลไม่ขึ้น | รอสถานะ **Running** แล้ว Refresh รายการเคอร์เนล |

## ล้างทรัพยากรเมื่อเลิกใช้

1. ซ้ายมือเลือก **Compute**
2. เลือกเครื่องของคุณ
3. เลือก **Stop**
