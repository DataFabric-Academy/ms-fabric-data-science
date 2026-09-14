# โน้ตผู้สอน: Automated ML เป็นเส้นหลัก

ผู้เรียนเดิน [แบบฝึกหัด 3](03-automl-classification.md) **เอง** บน Azure Machine Learning studio  
เอกสารนี้เป็นจังหวะห้องและประโยคที่ต้องพูด ไม่ใช่ demo คนเดียวบนจอผู้สอน

โครงเทียบเคียง Learn: AutoML นำ แล้ว MLflow ใน notebook เป็นงานเสริม  
อ้างอิง: [Find the best classification model with Automated Machine Learning](https://learn.microsoft.com/training/modules/find-best-classification-model-automated-machine-learning/) · [AI-300 study guide](https://learn.microsoft.com/credentials/certifications/resources/study-guides/ai-300)

## จุดประสงค์ในห้อง

ผู้เรียนตั้งงาน Classification บนชั้น Silver ได้ เลือกเมตริก AUC และลงทะเบียน Champion โดยไม่ Deploy

ประโยคปิดที่ต้องพูด:

> AutoML หาโมเดลเส้นฐานให้เร็ว แต่คุณยังต้องเลือกเมตริก กันข้อมูลรั่วไหล และตัดสินใจเองว่าจะขึ้นโมเดลไหนเข้าแคมเปญ

## ก่อนเปิดจอ

- เดินแบบฝึกหัด 2 บน workspace ผู้สอนให้หน้า **Data** มี `silver-customer-features`
- ตรวจโควตา compute ของ subscription ที่ใช้สอน
- ตัดสินใจล่วงหน้า: ทั้งคลาสใช้ **compute instance ของตนเอง** หรือผู้สอนเปิด **Serverless** เป็นแผนสำรอง
- อย่าให้ทั้งคลาสสร้าง compute cluster พร้อมกัน

## กติกาที่ผู้สอนต้องย้ำ

| ทำ | ห้าม |
| :--- | :--- |
| ชื่อ Champion = `freshmart-churn-model` | Deploy web service / Online endpoint |
| ตัด `CustomerID` ออก | เปิด Best Fit แบบไม่จำกัดเวลา |
| Primary metric = **AUC_weighted** | ทับชื่อโมเดลจากงานเสริม MLflow |
| Max trials 5 / timeout 20 นาที | สัญญาว่า AutoML ต้องชนะ Random Forest ทุกครั้ง |

## จังหวะแนะนำ (ประมาณ 40 นาที รวมรอจ็อบ)

| นาที | ผู้สอนทำ | ผู้เรียนทำ |
| :---: | :--- | :--- |
| 0–5 | โยงจากแบบฝึกหัด 2: ทำไมห้าม scale จากชุดทำนาย | เปิดตัวช่วย **Automated ML** |
| 5–15 | เดินจอตั้ง Classification แล้วเลือก Data asset `silver-customer-features` | กรอก experiment / เลือก asset / limits ตามตาราง |
| 15–25 | เดินรอที่แท็บ **Models** อธิบายว่าแต่ละแถวคือหนึ่ง trial | ส่งงาน แล้วดูสถานะ |
| 25–35 | ชี้ Register ไม่ใช่ Deploy | ลงทะเบียน `freshmart-churn-model` |
| 35–40 | ถามห้องหนึ่งข้อ แล้วส่งแบบฝึกหัด 4 | เปิด [04-batch-predict.md](04-batch-predict.md) |

ถ้าจ็อบช้า: ให้เปิด `03-automl-classification.ipynb` ทางสำรอง FLAML ทันที อย่ารอสร้าง cluster กลางคาบ

## คำถามปิดที่ควรได้ยินคำตอบ

- ถ้า AutoML ได้ AUC สูง จะขึ้นแคมเปญโดยไม่ดู Precision / Recall ได้ไหม
- ทำไมยังต้องมี `feature_params.json` จากแบบฝึกหัด 2
- ทำไมแทร็กฉุกเฉินนี้ไม่ให้กด Deploy

## งานเสริมหลังคาบ

เฉพาะคนที่แบบฝึกหัด 3 ผ่านแล้ว: [03-train-track-mlflow.md](03-train-track-mlflow.md)  
ลงทะเบียนเป็น `freshmart-churn-manual` เท่านั้น

## ผ่านคาบเมื่อ (ผู้สอน)

- [ ] ทั้งคลาสตั้ง Classification + เป้า `Churn` + ตัด `CustomerID`
- [ ] มี Champion ชื่อ `freshmart-churn-model` จาก AutoML
- [ ] ไม่มี Online endpoint ถูกสร้าง
- [ ] ห้องได้ยินประโยคปิดเรื่องเมตริกและข้อมูลรั่วไหล
- [ ] ส่งต่อแบบฝึกหัด 4 ด้วยโมเดลจาก AutoML
