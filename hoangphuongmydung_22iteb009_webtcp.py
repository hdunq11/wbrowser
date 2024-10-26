import sys
import requests
from PyQt6 import QtWidgets, QtWebEngineWidgets, QtCore
from bs4 import BeautifulSoup

class BrowserApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Web Browser")
        self.setGeometry(100, 100, 1200, 800)

        # Tạo web view
        self.browser = QtWebEngineWidgets.QWebEngineView()
        self.setCentralWidget(self.browser)

        # Tạo thanh điều hướng
        self.nav_bar = QtWidgets.QToolBar()
        self.addToolBar(self.nav_bar)

        # Thêm nút quay lại
        self.back_btn = QtWidgets.QPushButton("Back", self)
        self.back_btn.clicked.connect(self.browser.back)
        self.nav_bar.addWidget(self.back_btn)

        # Thêm nút tiến
        self.forward_btn = QtWidgets.QPushButton("Forward", self)
        self.forward_btn.clicked.connect(self.browser.forward)
        self.nav_bar.addWidget(self.forward_btn)

        # Thêm nút tải lại
        self.reload_btn = QtWidgets.QPushButton("Reload", self)
        self.reload_btn.clicked.connect(self.browser.reload)
        self.nav_bar.addWidget(self.reload_btn)

        # Tạo trường nhập URL
        self.url_input = QtWidgets.QLineEdit()
        self.url_input.returnPressed.connect(self.load_url)
        self.nav_bar.addWidget(self.url_input)

        # Thêm combobox chọn phương thức
        self.method_combo = QtWidgets.QComboBox()
        self.method_combo.addItems(["GET", "POST", "HEAD"])
        self.nav_bar.addWidget(self.method_combo)
        
        # Tạo QTextEdit để người dùng nhập dữ liệu POST
        self.post_data_input = QtWidgets.QTextEdit(self)
        self.post_data_input.setPlaceholderText("Enter POST data here...")
        self.post_data_input.setFixedHeight(50)  # Đặt chiều cao nhỏ hơn cho khung nhập liệu POST
        self.nav_bar.addWidget(self.post_data_input)

        # Tạo nút gửi yêu cầu
        self.send_button = QtWidgets.QPushButton("Send Request")
        self.send_button.clicked.connect(self.send_request)
        self.nav_bar.addWidget(self.send_button)
        
        # Tạo nút xem lịch sử
        self.history_btn = QtWidgets.QPushButton("History", self)
        self.history_btn.clicked.connect(self.show_history)
        self.nav_bar.addWidget(self.history_btn)

        # Tạo kết nối để cập nhật URL khi trang web thay đổi
        self.browser.urlChanged.connect(self.update_url)

        # Tạo danh sách lưu lịch sử duyệt web
        self.history = []


    def load_url(self):
        url = self.url_input.text()
        if not url.startswith('https'):
            url = 'https://' + url  # Thêm 'http://' nếu không có
        self.browser.setUrl(QtCore.QUrl(url))

    def send_request(self):
        url = self.url_input.text()
        if not url.startswith('https'):
            url = 'https://' + url

        method = self.method_combo.currentText()

        try:
            if method == "GET":
                response = requests.get(url)
                self.analyze_html(response.text)
                self.analyze_html(response.text)
                self.load_url()
            elif method == "POST":
                post_data = self.post_data_input.toPlainText()  # Lấy dữ liệu POST từ QTextEdit
                # Chuyển dữ liệu POST thành từ điển (key-value) nếu cần
                post_data_dict = dict(x.split('=') for x in post_data.split('&') if '=' in x)
                response = requests.post(url, data=post_data_dict)
                self.analyze_html(response.text)
            elif method == "HEAD":
                response = requests.head(url)
                self.show_head_info(response.headers)

        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Failed to perform {method} request: {e}")

    def analyze_html(self, html):
        # Phân tích HTML với BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        # Đếm các thẻ HTML
        # len = len(html)
        num_p_tags = len(soup.find_all('p'))
        num_div_tags = len(soup.find_all('div'))
        num_span_tags = len(soup.find_all('span'))
        num_img_tags = len(soup.find_all('img'))

        # Hiển thị kết quả
        # analysis_result.delete(1.0, 'end')
        # analysis_result.insert('end', f"HTML Length: {len} characters\n")
        analysis_result = f"Length of HTML: {len(html)} characters\n"
        analysis_result += f"<p> tags: {num_p_tags}\n"
        analysis_result += f"<div> tags: {num_div_tags}\n"
        analysis_result += f"<span> tags: {num_span_tags}\n"
        analysis_result += f"<img> tags: {num_img_tags}"
        analysis_result += "HTML Code:\n"
        analysis_result += html[:5000]

        QtWidgets.QMessageBox.information(self, "HTML Analysis", analysis_result)

    def show_head_info(self, headers):
        # Hiển thị thông tin về tài nguyên khi thực hiện HEAD request
        headers_info = "\n".join([f"{key}: {value}" for key, value in headers.items()])
        QtWidgets.QMessageBox.information(self, "HEAD Request Info", headers_info)

    def update_url(self, q):
        current_url = q.toString()
        self.url_input.setText(current_url)
        if current_url not in self.history:
            self.history.append(current_url)  # Thêm URL vào lịch sử

    def show_history(self):
        history_dialog = QtWidgets.QDialog(self)
        history_dialog.setWindowTitle("Browsing History")
        history_dialog.setGeometry(300, 300, 600, 400)

        layout = QtWidgets.QVBoxLayout()
        
        history_list = QtWidgets.QListWidget()
        history_list.addItems(self.history)
        layout.addWidget(history_list)

        # Tải lại trang khi người dùng chọn URL từ danh sách lịch sử
        history_list.itemClicked.connect(lambda item: self.browser.setUrl(QtCore.QUrl(item.text())))

        history_dialog.setLayout(layout)
        history_dialog.exec()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = BrowserApp()
    window.show()
    sys.exit(app.exec())
