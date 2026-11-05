<div align="center">
  <img src="static/img/logo.png" alt="GreaterWMS logo" width="200" height="auto" />
  <h1>GreaterWMS</h1>
  <h3>Open Source Warehouse Management System — Customized for Your Business</h3>
</div>

> ## 🎉 GreaterWMS 3.0 Released · Rebuilt with Bomiot
>
> GreaterWMS 3.0 is now officially released, with its core fully **rebuilt** using [Bomiot](https://github.com/Bomiot/Bomiot). The Rust-based plugin architecture and app marketplace make custom development and feature extension more efficient.
>
> 👉 **[Visit Bomiot to Learn More](https://github.com/Bomiot/Bomiot)**



## 🎬 Open Source Version Feature Video

Want to quickly understand what GreaterWMS can do? We've recorded a complete open-source feature demo, covering core workflows such as inbound, outbound, inventory management, and PDA scanning.

👉 **[Watch the GreaterWMS Open Source Version Feature Video](https://www.bilibili.com/video/BV1r1Em6QE5v/?vd_source=e27ed0e4cbc69fce7cb662cddc3ceae1)**

## 🔓 Why Choose GreaterWMS

Traditional commercial WMS software is often closed-source and difficult to extend with secondary development. Once an enterprise chooses such software, secondary development becomes bound to the original vendor, with high costs and long cycles. GreaterWMS was created to solve this problem — the author has worked in the supply chain industry for 15 years and knows firsthand that the industry lacks a **highly flexible, highly customizable** solution to deeply support enterprise business. GreaterWMS is designed **for customization**: whether you only need to build inventory or warehouse management, or need to integrate with IoT, ERP, and distribution systems, GreaterWMS can serve as your foundation platform.

**Powered by the Bomiot Framework**

GreaterWMS 3.0 is now officially released, with its core fully **rebuilt** using [Bomiot](https://github.com/Bomiot/Bomiot). Bomiot's core is written in Rust, providing a plugin-based architecture, an app marketplace (extend via `pip install`), signal mechanisms, and more, making **custom development and feature extension more efficient**. It builds a new CLI-based software model that eliminates the need for manual environment configuration, making delivery more direct and efficient.

👉 **[Visit Bomiot to Explore the Plugin Marketplace and Developer Docs](https://github.com/Bomiot/Bomiot)**

**Developer Documentation**

All developer documentation has been migrated to [Bomiot](https://github.com/Bomiot/Bomiot). Install it with the following command:

```shell
pip install bomiot
```

## 🎯 Customization Capabilities

**API-First Backend**

This repository provides a Django REST Framework backend with REST-style APIs and interactive API documentation. Clients can be developed and deployed independently and connect to the backend over HTTP.

**Modular Business Design**

The system organizes business logic by module (ASN receiving, DN shipping, inventory, storage locations, etc.), with each module having clear responsibilities. You can **modify or extend only the modules you need** without affecting other features.

**Flexible Client Integration**

The APIs can be consumed by web, mobile, PDA, ERP, or other client applications. This repository does not include those frontend clients.

## 📦 Real-World Customization Scenarios

GreaterWMS has been successfully customized and deployed across multiple industries:

**Third-Party Logistics & Cloud Warehouses (3PL)**: Based on the native code, extended multi-warehouse cluster management, one-truck multi-warehouse sequential loading/unloading, cold-chain IoT temperature control, batch expiry management, multi-tenant cargo-owner isolation, and more. Native Milk-Run capabilities can be adapted so that line-haul vehicles stop at multiple warehouses sequentially for loading and unloading.

**Pharmaceutical Distribution**: A custom batch management module enables automatic drug expiry alerts and integrates with IoT devices to monitor temperature and humidity, meeting GSP compliance requirements. After one pharmaceutical distribution enterprise went live, inventory turnover days dropped from 45 to 28.

**Cold-Chain Warehousing**: Added temperature recording and alerting on top of the standard WMS, achieving full-chain temperature control traceability across cold storage and refrigerated trucks.

**Cross-Border E-Commerce**: Developed international logistics and customs declaration integration interfaces to adapt to the special process needs of cross-border business.

**Manufacturing**: Satisfied component traceability needs through batch management and FIFO control, and integrated with MES systems to implement pull-based material management. After an automotive parts enterprise adopted it, inventory turnover improved by 25%.

## 🧭 Functionality in This Codebase

GreaterWMS is a warehouse operations system that tracks goods from receiving through storage, inventory checks, picking, and shipping. This repository contains the Django REST Framework backend; frontend clients are not included.

### Core warehouse workflows

- **Receiving:** Create advance shipping notices (ASNs), record received quantities, sort goods, move them into bins, and review shortages or overages.
- **Shipping:** Create delivery notes (DNs), release orders, prepare picking work, record picked quantities, dispatch shipments, and capture proof of delivery.
- **Inventory:** View stock by item or bin, inspect empty and occupied bins, and track quantities in states such as on-hand, held, damaged, inbound, picking, and back order.
- **Cycle counting:** Run cycle counts or manual counts, record physical quantities, and compare them with expected quantities.
- **Barcode scanning:** The API includes scanner-related endpoints that external mobile/PDA clients can use.

### Supporting features

- **Catalog and warehouse setup:** Manage goods and product attributes, warehouses, bins, bin sizes, and bin properties.
- **Business partners and staff:** Maintain suppliers, customers, companies, staff, staff types, drivers, and dispatch records.
- **Operations and reporting:** View inbound/outbound dashboards, count records, and customer proof-of-delivery screens.
- **Data exchange and finance-related records:** Import or export selected master and operational data; maintain capital/item records and transportation fee rates.

Backend API endpoints are grouped by Django app, with ASN, DN, stock, and cycle-count routes in `asn/urls.py`, `dn/urls.py`, `stock/urls.py`, and `cyclecount/urls.py`. Open `/api/docs/` for the interactive API documentation.

### Scope notes

- The source present in this repository reports version **2.1.48** in the Django settings. The README's GreaterWMS 3.0/Bomiot announcement may describe a newer release than this checkout.
- Cycle counts record quantity differences, but this codebase does not appear to include a dedicated lost-item investigation ticket workflow with assignment, investigation notes, and resolution outcomes.
- The finance-related screens cover capital and transportation fees; they should not be mistaken for a full accounting system.

## 🧭 Quick Start

### Get the Code

```bash
git clone https://github.com/GreaterWMS/GreaterWMS.git
cd GreaterWMS
```

### Backend Startup

```bash
pip install -r requirements.txt
daphne -b 0.0.0.0 -p 8008 greaterwms.asgi:application
```

### Tech Stack

- **Backend**: Python 3.8+ / Django 3.1+ / Django REST Framework
- **Database**: SQLite (default) / MySQL / PostgreSQL

## 📬 Contact

**Official Website**: [https://www.bomiot.com/](https://www.bomiot.com/)

**Email**: dawnup888@163.com

**WeChat**: ts-Wlm

If you have customization needs, business cooperation intentions, or wish to consult about secondary development, feel free to contact us through the channels above.

## License

Apache 2.0
