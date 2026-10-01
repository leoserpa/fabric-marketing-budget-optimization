# Report Layout Templates (Power BI)

> Custom vector SVG canvas background layouts developed specifically for the analytical pages of the Power BI report within Microsoft Fabric.

[Português](README.md) | [English](README.en.md)

---

## Overview

This directory stores the canvas background templates used across the **Marketing Budget Optimization** report suite. Rather than assembling containers, divider lines, and card shapes using dozens of individual Power BI native shape elements, the report utilizes **standalone vector SVG templates**.

### Key Advantages of SVG Templates:
1. **Report Rendering Performance:** Significantly reduces internal Document Object Model (DOM) overhead by replacing dozens of native shapes with a single vector layer, speeding up visual execution and DirectLake queries.
2. **Absolute Vector Crispness:** Being purely vector-based, SVG maintains razor-sharp lines and geometric proportions across any display resolution (Full HD, 2K, 4K) without pixelation or compression artifacts.
3. **Minimal Storage Footprint:** Extremely lightweight assets (under 10 KB each), optimizing repository size and Git version control workflows.
4. **Design Consistency:** Enforces standardized padding, visual hierarchy, and an enterprise dark mode palette consistently across all pages.

---

## File Catalog

| File | Target Page | Recommended Dimensions | Description |
|:---|:---|:---:|:---|
| `template-pagina-1-executivo.svg` | **1. Executive** | 1920 x 2160 px (Vertical scroll) | Layout for executive KPIs, 4 analytical core blocks (return & acquisition costs), and full-width timeline chart. |
| `template-pagina-2-campanhas.svg` | **2. Campaigns** | 1920 x 2160 px (Vertical scroll) | Performance grid featuring conversion rates (Conversion Rate, CTR), placement matrices, and tactical drill-down table. |
| `template-pagina-3-orcamento.svg` | **3. Budget** | 1920 x 2160 px (Vertical scroll) | Decision-oriented layout: efficiency allocation, budget misalignment analysis, and ad spend re-allocation matrix. |

---

## Setup Instructions in Power BI Desktop

Follow these exact steps to apply the templates with proper alignment and vertical scroll:

1. **Configure Custom Page Dimensions:**
   - Select the target report page.
   - Open the **Format report page** pane > **Canvas settings**.
   - Set **Type** to **Custom**.
   - Configure dimensions: **Width: 1920 px** and **Height: 2160 px**.

2. **Configure View Mode (Vertical Scrolling):**
   - In the top ribbon of Power BI Desktop, open the **View** tab.
   - In the **Page view** dropdown, select **Fit to width**. This enables smooth vertical scroll navigation.

3. **Apply the Background Template:**
   - In the **Format report page** pane, expand **Canvas background**.
   - Click **Browse** in the image section and select the corresponding file from `assets/templates/`.
   - Set **Image fit** to **Fit** or **Fill**.
   - Set **Transparency strictly to 0%** (Power BI defaults to 100%, which makes the image transparent).

4. **Visual Transparency:**
   - To let the card containers and design structure show through cleanly, select each visual/chart/table and ensure that the **Visual background** is turned off or set to **100% transparency**.

---

[Back to Main Repository](../../README.md)
