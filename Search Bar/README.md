# Deskime SearchBar
<div style="text-align: center;"> 

![Screenshot](./screenshot.png)

A Custom Search / Command Bar made with Python.
</div>

------------

## Features

-  **Web Search**: It is pinned in the top-left corner of your desktop. You can set any website on it.
<br><br>
-  **Calculation**: It has calculation abilities to know if a math operation is provided in the search

### Tested On

- **Python Version**: Python 3.10 (64-bit)

### Prerequisites

- [x] Python 3.8 or higher
- [x] Pythonw (typically installed with Python, used for console-less execution)
- [x] pip
- [x] Windows 10 or higher (currently not supported on Mac)

## Setup

1. ⭐ `Clone` this repository branch
	  <br><br>
2.  Install the necessary dependencies mentioned in the main branch of this repository.
  <br><br>

3. Customize as needed
<br><br>
4. Run `webwidget.pyw`

### Customizing the App

- Editing the webwidget.pyw website.


```python
self.web_view.setUrl(QUrl.fromLocalFile(html_file))  # Load ann HTML file as QUrl
self.web_view.setUrl(QUrl("https://yoururl.com"))  # Load a Website as QUrl
```

### Support Us
If you appreciate our initiative, consider buying us a coffee to help keep this program open-source and accessible to more users.
<br><br>