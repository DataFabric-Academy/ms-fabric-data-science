# แหล่งอ้างอิง — Fabric Data Science

## Microsoft Learn — Learning Path

**Implement a data science and machine learning solution for AI in Microsoft Fabric**  
https://learn.microsoft.com/training/paths/implement-data-science-machine-learning-fabric/

| โมดูล | URL |
| --- | --- |
| Introduction to end-to-end analytics using Microsoft Fabric | https://learn.microsoft.com/training/modules/introduction-end-analytics-use-microsoft-fabric/ |
| Get started with data science in Microsoft Fabric | https://learn.microsoft.com/training/modules/get-started-data-science-fabric/ |
| Explore data for data science with notebooks | https://learn.microsoft.com/training/modules/explore-data-for-data-science-microsoft-fabric/ |
| Preprocess data with Data Wrangler | https://learn.microsoft.com/training/modules/preprocess-data-with-data-wrangler-microsoft-fabric/ |
| Train and track models with MLflow | https://learn.microsoft.com/training/modules/train-track-model-fabric/ |
| Generate batch predictions | https://learn.microsoft.com/training/modules/generate-batch-predictions-fabric/ |

## สภาพแวดล้อมแล็บ (ผู้เรียนสร้างเอง)

แต่ละคนลงทะเบียน Trial และสร้าง workspace ของตนเอง — ไม่เชิญใครเข้า

| หัวข้อ | URL |
| --- | --- |
| Fabric Trial 60 วัน | https://learn.microsoft.com/fabric/fundamentals/fabric-trial |
| สร้าง workspace | https://learn.microsoft.com/fabric/fundamentals/create-workspaces |
| สร้าง lakehouse (เปิด schemas) | https://learn.microsoft.com/fabric/data-engineering/create-lakehouse |

## เอกสารผลิตภัณฑ์ Fabric (เชิงลึก)

| หัวข้อ | URL |
| --- | --- |
| What is Data Science in Fabric? | https://learn.microsoft.com/fabric/data-science/data-science-overview |
| End-to-end tutorial hub | https://learn.microsoft.com/fabric/data-science/tutorial-data-science-introduction |
| Data Wrangler | https://learn.microsoft.com/fabric/data-science/data-wrangler |
| ML experiments | https://learn.microsoft.com/fabric/data-science/machine-learning-experiment |
| ML models | https://learn.microsoft.com/fabric/data-science/machine-learning-model |
| PREDICT scoring | https://learn.microsoft.com/fabric/data-science/model-scoring-predict |
| Semantic Link | https://learn.microsoft.com/fabric/data-science/semantic-link-overview |
| MLflow autologging | https://learn.microsoft.com/fabric/data-science/mlflow-autologging |

## สไลด์ใน repo (โฟลเดอร์ `Source/` — ไม่ติด git ตาม `.gitignore`)

| ไฟล์ | เนื้อหา |
| --- | --- |
| `DP-604-TH-12H-DataScience-Fabric.pptx` | Instructor Edition ภาษาไทย ~120 สไลด์ (M00–M08) |
| `DP-604T00-ENU-PowerPoint_01.pptx` | Courseware ENU หลัก |
| `DP-604T00-ENU-PowerPoint_00-Introduction.pptx` | Introduction deck |
| `DP-604T00-ENU-PowerPoint_02-Conclusion.pptx` | Conclusion deck |
| `slides_m00_m01.py` … `slides_m06_m08.py` | ซอร์สสร้างสไลด์ไทย |
| `กำหนดการ_Final.pdf` | กำหนดการอบรม |

## แล็บใน repo นี้

| Lab | คู่มือ | Notebook |
| --- | --- | --- |
| 0 | [instructions/00-lakehouse-setup.md](../labs/instructions/00-lakehouse-setup.md) | `00-environment-verification.ipynb` |
| 1 | [instructions/01-explore-data.md](../labs/instructions/01-explore-data.md) | `01-explore-data.ipynb` |
| 2 | [instructions/02-preprocess-data-wrangler.md](../labs/instructions/02-preprocess-data-wrangler.md) | `02-preprocess-data-wrangler.ipynb` |
| 3 | [instructions/03-train-track-mlflow.md](../labs/instructions/03-train-track-mlflow.md) | `03-train-track-mlflow.ipynb` |
| 4 | [instructions/04-batch-predict.md](../labs/instructions/04-batch-predict.md) | `04-batch-predict.ipynb` |

เริ่มที่ [labs/README.md](../labs/README.md)

## การแมป Docs กับสไลด์และ Learn

ดูตารางใน [docs/README.md](README.md)

- อภิธานศัพท์สำหรับผู้เรียน: [glossary.md](glossary.md)  
- มาตรฐานภาษาไทย: [writing-style-th.md](writing-style-th.md)
