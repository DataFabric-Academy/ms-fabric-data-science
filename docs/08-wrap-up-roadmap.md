# M08 — สรุปหลักสูตรและแผนนำไปใช้ 30 วัน

อ้างอิง: สไลด์ M08 · [Learning Path — Implement data science & machine learning for AI in Fabric](https://learn.microsoft.com/training/paths/implement-data-science-machine-learning-fabric/)

หลังอ่านบทนี้ คุณจะทบทวนทักษะที่ได้ และวางแผน 30 วันแรกในการนำ Fabric ไปใช้กับโจทย์องค์กร  
ศัพท์ที่เกี่ยวข้อง: [glossary.md](glossary.md)

## สิ่งที่หลักสูตรพาเดินครบวงจร

ลำดับงานที่คุณได้ทำตลอดหลักสูตร:

1. เริ่มจากโจทย์ธุรกิจ FreshMart  
2. เก็บข้อมูลบน OneLake ในชั้นดิบ (Bronze)  
3. สำรวจข้อมูลบน Notebook (Lab 1)  
4. ใช้ Data Wrangler สร้างฟีเจอร์ชั้น Silver (Lab 2)  
5. ทดลองด้วย MLflow แล้วลงทะเบียนโมเดล (Lab 3)  
6. ใช้ PREDICT เขียนคำทำนายชั้น Gold แล้วเปิดรายงาน (Lab 4)  
7. ทบทวน Copilot, Semantic Link, Responsible AI และการดูแล Capacity  

## Checklist ทักษะหลังเรียน

### ลงมือทำได้

- [ ] แนบ Lakehouse และอ่านตาราง Delta ใน Notebook  
- [ ] สำรวจข้อมูล: ค่าว่าง, การกระจายตัว, ความสัมพันธ์ระหว่างตัวแปร  
- [ ] ใช้ Data Wrangler แล้วเพิ่มโค้ดเข้า notebook  
- [ ] แบ่งชุดฝึก / ชุดปรับแต่ง / ชุดทดสอบ อย่างมีวินัย  
- [ ] ติดตามการรันด้วย MLflow และเปรียบเทียบเมตริก (เช่น AUC — ดู [glossary](glossary.md#auc-area-under-the-roc-curve))  
- [ ] ลงทะเบียนโมเดลพร้อมลายเซ็นโครงสร้างข้อมูล  
- [ ] สร้างคำทำนายเป็นชุดด้วย PREDICT หรือ `MLFlowTransformer`  
- [ ] เขียนผลลงตาราง Gold สำหรับแคมเปญหรือรายงาน  

### ตัดสินใจเชิงสถาปัตยกรรมได้

- [ ] เลือกจำแนกประเภท / ถดถอย / จัดกลุ่ม / พยากรณ์อนุกรมเวลา ได้ตรงโจทย์  
- [ ] อธิบายแนวอ่านสำเนาเดียวบน OneLake และบทบาท Lakehouse กับงานวิทยาศาสตร์ข้อมูล  
- [ ] แยกการทำนายเป็นชุดกับการทำนายแบบทันที ตามจังหวะธุรกิจ  
- [ ] ระบุจุดเสี่ยงข้อมูลรั่วไหลเข้าโมเดล และการกำกับดูแลหลังขึ้นระบบ  

## แผนปฏิบัติการ 30 วัน

| ช่วง | เป้าหมาย |
| --- | --- |
| สัปดาห์ที่ 1 | เลือกโจทย์ธุรกิจ 1 ข้อ นิยามตัวชี้วัดสำเร็จ และสำรวจข้อมูลที่มีใน OneLake หรือแหล่งจริง |
| สัปดาห์ที่ 2 | สร้าง Lakehouse ชั้น Bronze–Silver ขั้นต่ำ เปิด Notebook สำรวจข้อมูล และร่างฟีเจอร์ |
| สัปดาห์ที่ 3 | ฝึกโมเดลเส้นฐานด้วย MLflow อย่างน้อย 2 อัลกอริทึม เปรียบเทียบบนชุดปรับแต่งและชุดทดสอบ |
| สัปดาห์ที่ 4 | ทำนายเป็นชุดเข้าตาราง Gold สร้างแดชบอร์ดบางส่วน และทบทวน Responsible AI / สิทธิ์ / ตารางฝึกใหม่ |

คำถามนำทาง: **โจทย์แรกที่คุณจะนำโมเดลสู่ปฏิบัติการคืออะไร — ทำนายสิ่งใด เพื่อให้ใครตัดสินใจอะไร**

## เส้นทางเรียนรู้ต่อ

1. ทำ Learning Path ให้ครบ: [Implement data science & machine learning for AI in Fabric](https://learn.microsoft.com/training/paths/implement-data-science-machine-learning-fabric/)  
2. ทำ tutorial ทางการแบบครบวงจร: [Data science scenario](https://learn.microsoft.com/fabric/data-science/tutorial-data-science-introduction)  
3. ต่อยอด Lakehouse / Spark / ธรรมาภิบาลตามบทบาท  
4. ดูเส้นทางใบรับรองที่เกี่ยวข้องกับ Fabric ตามบทบาทปัจจุบันบน Microsoft Learn  

## กลับไปปฏิบัติ

- ดัชนี docs: [README.md](README.md)  
- อภิธานศัพท์: [glossary.md](glossary.md)  
- มาตรฐานภาษา: [writing-style-th.md](writing-style-th.md)  
- Labs: [../labs/README.md](../labs/README.md)  
- แหล่งอ้างอิงเต็ม: [resources.md](resources.md)
