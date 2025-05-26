import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
from PIL import Image
from PIL.ExifTags import TAGS
import threading

class MetadataRemover:
    def __init__(self, root):
        self.root = root
        self.root.title("이미지 메타데이터 제거 도구")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # 메인 프레임
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 제목
        title_label = ttk.Label(main_frame, text="이미지 메타데이터 제거 도구", 
                               font=("맑은 고딕", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 파일 선택 영역
        file_frame = ttk.LabelFrame(main_frame, text="파일 선택", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(file_frame, text="단일 파일 선택", 
                  command=self.select_single_file).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(file_frame, text="여러 파일 선택", 
                  command=self.select_multiple_files).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(file_frame, text="폴더 선택", 
                  command=self.select_folder).grid(row=0, column=2)
        
        # 선택된 파일 목록
        list_frame = ttk.LabelFrame(main_frame, text="선택된 파일", padding="10")
        list_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 리스트박스와 스크롤바
        self.file_listbox = tk.Listbox(list_frame, height=10)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.file_listbox.yview)
        self.file_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.file_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 리스트 조작 버튼
        list_btn_frame = ttk.Frame(list_frame)
        list_btn_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(list_btn_frame, text="선택 삭제", 
                  command=self.remove_selected).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(list_btn_frame, text="전체 삭제", 
                  command=self.clear_list).grid(row=0, column=1)
        
        # 옵션 영역
        option_frame = ttk.LabelFrame(main_frame, text="옵션", padding="10")
        option_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.overwrite_var = tk.BooleanVar()
        self.backup_var = tk.BooleanVar(value=True)
        self.custom_output_var = tk.BooleanVar()
        
        ttk.Checkbutton(option_frame, text="원본 파일 덮어쓰기", 
                       variable=self.overwrite_var, command=self.toggle_output_options).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(option_frame, text="원본 백업 생성", 
                       variable=self.backup_var).grid(row=0, column=1, sticky=tk.W, padx=(20, 0))
        
        # 출력 폴더 선택
        output_frame = ttk.Frame(option_frame)
        output_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Checkbutton(output_frame, text="출력 폴더 지정:", 
                       variable=self.custom_output_var, command=self.toggle_output_options).grid(row=0, column=0, sticky=tk.W)
        
        self.output_path_var = tk.StringVar(value="원본과 같은 폴더")
        self.output_label = ttk.Label(output_frame, textvariable=self.output_path_var, 
                                     relief="sunken", width=50)
        self.output_label.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 5))
        
        self.output_btn = ttk.Button(output_frame, text="폴더 선택", 
                                    command=self.select_output_folder, state='disabled')
        self.output_btn.grid(row=0, column=2)
        
        output_frame.columnconfigure(1, weight=1)
        
        self.output_folder = None
        
        # 실행 버튼과 진행률
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.process_btn = ttk.Button(action_frame, text="메타데이터 제거 실행", 
                                     command=self.start_processing)
        self.process_btn.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # 진행률 표시
        self.progress = ttk.Progressbar(action_frame, mode='determinate')
        self.progress.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.status_label = ttk.Label(action_frame, text="대기 중...")
        self.status_label.grid(row=1, column=1)
        
        # 로그 영역
        log_frame = ttk.LabelFrame(main_frame, text="처리 결과", padding="10")
        log_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.log_text = tk.Text(log_frame, height=8, wrap=tk.WORD)
        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 그리드 가중치 설정
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        main_frame.rowconfigure(5, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        action_frame.columnconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.file_paths = []
        
    def toggle_output_options(self):
        """출력 옵션에 따라 UI 상태 변경"""
        if self.overwrite_var.get():
            self.custom_output_var.set(False)
            self.output_btn.configure(state='disabled')
            self.output_path_var.set("원본 파일 덮어쓰기")
        elif self.custom_output_var.get():
            self.overwrite_var.set(False)
            self.output_btn.configure(state='normal')
            if not self.output_folder:
                self.output_path_var.set("출력 폴더를 선택해주세요")
        else:
            self.output_btn.configure(state='disabled')
            self.output_path_var.set("원본과 같은 폴더")
    
    def select_output_folder(self):
        """출력 폴더 선택"""
        folder_path = filedialog.askdirectory(title="처리된 파일을 저장할 폴더 선택")
        if folder_path:
            self.output_folder = folder_path
            self.output_path_var.set(folder_path)
    
    def select_single_file(self):
        """단일 이미지 파일 선택"""
        file_path = filedialog.askopenfilename(
            title="이미지 파일 선택",
            filetypes=[
                ("이미지 파일", "*.jpg *.jpeg *.png *.tiff *.tif *.bmp"),
                ("JPEG 파일", "*.jpg *.jpeg"),
                ("PNG 파일", "*.png"),
                ("TIFF 파일", "*.tiff *.tif"),
                ("모든 파일", "*.*")
            ]
        )
        if file_path:
            if file_path not in self.file_paths:
                self.file_paths.append(file_path)
                self.update_file_list()
    
    def select_multiple_files(self):
        """여러 이미지 파일 선택"""
        file_paths = filedialog.askopenfilenames(
            title="이미지 파일들 선택",
            filetypes=[
                ("이미지 파일", "*.jpg *.jpeg *.png *.tiff *.tif *.bmp"),
                ("JPEG 파일", "*.jpg *.jpeg"),
                ("PNG 파일", "*.png"),
                ("TIFF 파일", "*.tiff *.tif"),
                ("모든 파일", "*.*")
            ]
        )
        for file_path in file_paths:
            if file_path not in self.file_paths:
                self.file_paths.append(file_path)
        self.update_file_list()
    
    def select_folder(self):
        """폴더 내 모든 이미지 파일 선택"""
        folder_path = filedialog.askdirectory(title="이미지가 있는 폴더 선택")
        if folder_path:
            image_extensions = ('.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp')
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if file.lower().endswith(image_extensions):
                        file_path = os.path.join(root, file)
                        if file_path not in self.file_paths:
                            self.file_paths.append(file_path)
            self.update_file_list()
    
    def update_file_list(self):
        """파일 목록 업데이트"""
        self.file_listbox.delete(0, tk.END)
        for file_path in self.file_paths:
            self.file_listbox.insert(tk.END, os.path.basename(file_path))
    
    def remove_selected(self):
        """선택된 파일을 목록에서 제거"""
        selected_indices = self.file_listbox.curselection()
        for i in reversed(selected_indices):
            del self.file_paths[i]
        self.update_file_list()
    
    def clear_list(self):
        """파일 목록 전체 삭제"""
        self.file_paths.clear()
        self.update_file_list()
    
    def log_message(self, message):
        """로그 메시지 추가"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def remove_metadata(self, file_path):
        """단일 파일의 메타데이터 제거"""
        try:
            # 원본 백업
            if self.backup_var.get() and self.overwrite_var.get():
                backup_path = f"{file_path}.backup"
                with open(file_path, 'rb') as src, open(backup_path, 'wb') as dst:
                    dst.write(src.read())
            
            # 이미지 열기
            with Image.open(file_path) as img:
                # 이미지 데이터만 추출 (메타데이터 제외)
                clean_img = Image.new(img.mode, img.size)
                clean_img.putdata(list(img.getdata()))
                
                # 저장 경로 결정
                if self.overwrite_var.get():
                    output_path = file_path
                elif self.custom_output_var.get() and self.output_folder:
                    filename = os.path.basename(file_path)
                    name, ext = os.path.splitext(filename)
                    clean_filename = f"{name}_clean{ext}"
                    output_path = os.path.join(self.output_folder, clean_filename)
                else:
                    name, ext = os.path.splitext(file_path)
                    output_path = f"{name}_clean{ext}"
                
                # 메타데이터 없이 저장
                clean_img.save(output_path, quality=95, optimize=True)
                
            return True, output_path
            
        except Exception as e:
            return False, str(e)
    
    def start_processing(self):
        """메타데이터 제거 프로세스 시작"""
        if not self.file_paths:
            messagebox.showwarning("경고", "처리할 파일을 선택해주세요.")
            return
        
        self.process_btn.configure(state='disabled')
        self.log_text.delete(1.0, tk.END)
        
        # 별도 스레드에서 처리
        thread = threading.Thread(target=self.process_files)
        thread.daemon = True
        thread.start()
    
    def process_files(self):
        """파일들을 처리하는 메인 함수"""
        total_files = len(self.file_paths)
        processed = 0
        successful = 0
        
        self.progress.configure(maximum=total_files)
        self.log_message(f"총 {total_files}개 파일 처리 시작...")
        
        for i, file_path in enumerate(self.file_paths):
            filename = os.path.basename(file_path)
            self.status_label.configure(text=f"처리 중: {filename}")
            
            success, result = self.remove_metadata(file_path)
            processed += 1
            
            if success:
                successful += 1
                self.log_message(f"✓ {filename} - 메타데이터 제거 완료")
            else:
                self.log_message(f"✗ {filename} - 오류: {result}")
            
            self.progress.configure(value=processed)
            self.root.update_idletasks()
        
        # 완료 메시지
        self.status_label.configure(text="처리 완료")
        self.log_message(f"\n처리 완료: {successful}/{total_files} 성공")
        
        if successful == total_files:
            messagebox.showinfo("완료", f"모든 파일의 메타데이터가 성공적으로 제거되었습니다.\n처리된 파일: {successful}개")
        else:
            messagebox.showwarning("완료", f"일부 파일 처리 중 오류가 발생했습니다.\n성공: {successful}개, 실패: {total_files - successful}개")
        
        self.process_btn.configure(state='normal')

def main():
    root = tk.Tk()
    app = MetadataRemover(root)
    root.mainloop()

if __name__ == "__main__":
    main()