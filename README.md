# MeiliSearch Connector for Odoo 12 CE

A powerful and efficient Odoo 12 Community Edition module that integrates MeiliSearch for lightning-fast search capabilities on production lots and serial numbers.

[![License: LGPL v3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)
[![Odoo Version](https://img.shields.io/badge/Odoo-12.0-brightgreen.svg)](https://www.odoo.com/)
[![Python Version](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/)

## 🚀 Features

- **Real-time Synchronization**: Automatically indexes lots/serial numbers on create, update, and delete
- **Bulk Indexing**: Index thousands of existing records with a single click
- **Cloud Compatible**: Works seamlessly with MeiliSearch Cloud instances
- **Fast Search**: Search by lot name, product name, or SKU with millisecond response times
- **Batch Processing**: Efficiently handles large datasets with intelligent batching
- **Error Resilient**: Continues operations even if MeiliSearch is temporarily unavailable

## 📋 Requirements

- **Odoo**: 12.0 Community Edition
- **Python**: 3.6+
- **MeiliSearch**: Any version (tested with cloud instances)
- **Python Packages**: 
  - `requests>=2.20.0` (for direct HTTP API calls)

## 🔧 Installation

### 1. Install Python Dependencies

```bash
# Activate your Odoo virtual environment
source /opt/odoo/odoo12-venv/bin/activate

# Install required package (or use requirements.txt)
pip install requests

# Or install from requirements.txt
pip install -r requirements.txt
```

### 2. Install the Odoo Module

```bash
# Copy module to your Odoo addons directory
cp -r meili_connector_v12 /opt/odoo/odoo12/addons/

# Set correct ownership
sudo chown -R odoo:odoo /opt/odoo/odoo12/addons/meili_connector_v12

# Restart Odoo
sudo service odoo12 restart
```

### 3. Activate the Module

1. Log into Odoo as administrator
2. Go to **Apps** menu
3. Click **Update Apps List**
4. Search for "MeiliSearch Connector"
5. Click **Install**

## ⚙️ Configuration

### 1. Configure MeiliSearch Connection

1. Go to **Settings** (enable Developer Mode if needed)
2. Scroll to **MeiliSearch Configuration** section
3. Enter your configuration:
   - **MeiliSearch Host**: Your MeiliSearch server URL
     - Local: `http://localhost:7700`
     - Cloud: `https://your-instance.meilisearch.io`
   - **MeiliSearch Admin Key**: Your admin/master API key
4. Click **Save**

### 2. Verify Connection

The module will automatically test the connection when you save. Check the logs for any errors:

```bash
tail -f /var/log/odoo12/odoo.log | grep -i meili
```

## 📊 Usage

### Automatic Indexing

Once configured, the module automatically indexes lots when:
- A new lot is created
- An existing lot is updated
- A lot is deleted

### Bulk Indexing Existing Data

To index all existing lots in your database:

**Method 1: From Menu**
1. Go to **Inventory → Configuration → MeiliSearch → Bulk Index Lots**
2. Click to start indexing
3. A notification will appear when complete

**Method 2: From Lots List**
1. Go to **Inventory → Products → Lots/Serial Numbers**
2. Click **Action** menu (⚙️ icon)
3. Select **"MeiliSearch: Bulk Index All Lots"**

**Method 3: Python Console** (Developer Mode)
```python
env['stock.production.lot'].action_bulk_index_all_lots()
```

### Indexed Fields

For each lot/serial number, the following data is indexed:

| Field | Description |
|-------|-------------|
| `id` | Lot ID (string) |
| `lot_id` | Duplicate ID for convenience |
| `lot_name` | Lot/Serial number name |
| `product_id` | Associated product ID |
| `product_name` | Product name |
| `sku` | Product SKU (default_code) |
| `searchable_text` | Combined lot name + SKU for enhanced search |

### Searching via MeiliSearch

Once indexed, you can search through MeiliSearch:

**Example using MeiliSearch Cloud Dashboard:**
- Search for lots by name, product, or SKU
- Get instant results with typo tolerance
- Filter and facet as needed

**Example using API:**
```bash
curl -X POST 'https://your-instance.meilisearch.io/indexes/lots/search' \
  -H 'Authorization: Bearer YOUR_KEY' \
  -H 'Content-Type: application/json' \
  --data-binary '{"q": "LOT123"}'
```

## 🏗️ Architecture

The module uses **direct HTTP requests** via the `requests` library for maximum compatibility with all MeiliSearch versions and cloud instances. This approach:
- Works with any Python 3.6+ environment
- Compatible with all MeiliSearch versions
- No SDK version conflicts
- Simpler, more maintainable code

### Key Components

- **`meili_client.py`**: Connection testing and authentication
- **`document_mixin.py`**: Core indexing/deletion logic using direct HTTP API calls
- **`stock_production_lot.py`**: Lot-specific implementation with bulk indexing
- **`res_config_settings.py`**: Configuration interface

### Batch Processing

- **Batch Size**: 500 lots per batch
- **Delay**: 500ms between batches to avoid rate limiting
- **Timeout**: 30s for indexing, 10s for deletion
- **Error Handling**: Continues processing even if individual batches fail

## 🔍 Troubleshooting

### Connection Issues

**Problem**: `401 Unauthorized` errors

**Solution**: 
- Verify your API key is correct
- Ensure you're using the admin/master key (not search key)
- Check MeiliSearch server is accessible from Odoo server

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'requests'`

**Solution**:
```bash
source /opt/odoo/odoo12-venv/bin/activate
pip install requests
sudo service odoo12 restart
```

### Performance Issues

**Problem**: Bulk indexing is slow or times out

**Solution**:
- Check your MeiliSearch instance has adequate resources
- Monitor network latency between Odoo and MeiliSearch
- Consider reducing batch size in `stock_production_lot.py`

### View Logs

```bash
# Real-time log monitoring
tail -f /var/log/odoo12/odoo.log | grep -i meili

# Search for errors
grep "ERROR.*meili" /var/log/odoo12/odoo.log | tail -50
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/odoo-meilisearch-connector.git
cd odoo-meilisearch-connector

# Install in development mode
ln -s $(pwd)/meili_connector_v12 /opt/odoo/odoo12/addons/
```

## 📝 License

This project is licensed under the LGPL v3 License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [MeiliSearch](https://www.meilisearch.com/) - The powerful search engine
- [Odoo Community](https://www.odoo.com/forum) - For the amazing ERP platform

## 📧 Support

For issues, questions, or contributions:
- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/odoo-meilisearch-connector/issues)
- **Discussions**: [GitHub Discussions](https://github.com/YOUR_USERNAME/odoo-meilisearch-connector/discussions)

---

Made with ❤️ for the Odoo community

