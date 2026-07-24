from __future__ import annotations

import locale


LANGUAGE_LABELS = {
    "English": "en",
    "Türkçe": "tr",
}

FILTER_MODE_LABELS = {
    "en": {
        "contains": "Contains",
        "equals": "Equals",
        "not_equals": "Does not equal",
        "not_empty": "Is not empty",
        "empty": "Is empty",
    },
    "tr": {
        "contains": "İçerir",
        "equals": "Eşittir",
        "not_equals": "Eşit değildir",
        "not_empty": "Boş değildir",
        "empty": "Boştur",
    },
}

TRANSLATIONS = {
    "en": {
        "app_title": "Business Data Automation Studio",
        "app_subtitle": (
            "Import, validate, clean, filter, and export business data "
            "with reusable workflow profiles."
        ),
        "language": "Language:",
        "no_file": "No data file selected",
        "load_prompt": "Load a CSV, TXT, or XLSX file to begin.",
        "ready": "Ready.",
        "select_data_file": "Select Data File",
        "excel_worksheet": "Excel worksheet:",
        "data_preview": "Data Preview",
        "workflow_rules": "Workflow Rules",
        "export_log": "Export & Log",
        "show_source": "Show Source Data",
        "show_processed": "Show Processed Data",
        "cleaning_rules": "Cleaning Rules",
        "trim_whitespace": "Trim whitespace in every cell",
        "normalize_headers": "Normalize column headers",
        "remove_empty": "Remove completely empty rows",
        "remove_duplicates": "Remove duplicate rows",
        "validation": "Validation",
        "required_columns": "Required columns (comma-separated):",
        "row_filter": "Row Filter",
        "column": "Column:",
        "condition": "Condition:",
        "value": "Value:",
        "column_rename": "Column Rename",
        "current_column": "Current column:",
        "new_name": "New name:",
        "add_rename": "Add Rename Rule",
        "no_rename_rules": "No column rename rules.",
        "apply_workflow": "Apply Workflow",
        "save_profile": "Save Workflow Profile",
        "load_profile": "Load Workflow Profile",
        "clear_rules": "Clear Rules",
        "export_processed": "Export Processed Data",
        "export_csv": "Export CSV",
        "export_excel": "Export Excel",
        "export_json": "Export JSON",
        "export_validation": "Export Validation Report",
        "processing_log": "Processing Log",
        "select_data_title": "Select a CSV, TXT, or Excel data file",
        "supported_files": "Supported data files",
        "excel_workbooks": "Excel workbooks",
        "csv_files": "CSV files",
        "text_files": "Text files",
        "all_files": "All files",
        "file_error": "File Error",
        "data_loaded_status": (
            "Data loaded. Configure and apply workflow rules."
        ),
        "log_loaded_file": "Loaded data file: {name}",
        "log_selected_sheet": "Selected Excel worksheet: {sheet}",
        "worksheet_error": "Worksheet Error",
        "worksheet_loaded_status": (
            "Worksheet loaded: {sheet}. Configure workflow rules."
        ),
        "file_info_excel": (
            "{rows} row(s), {columns} column(s) · Excel worksheet: {sheet}"
        ),
        "file_info_text": (
            "{rows} row(s), {columns} column(s) · "
            "Encoding: {encoding} · Delimiter: {delimiter}"
        ),
        "delimiter_comma": "comma",
        "delimiter_semicolon": "semicolon",
        "delimiter_tab": "tab",
        "delimiter_pipe": "pipe",
        "workflow_error": "Workflow Error",
        "log_workflow_completed": (
            "Workflow completed: {rows} output row(s), "
            "{duplicates} duplicate(s) removed, "
            "{issues} validation issue(s)."
        ),
        "workflow_complete_status": (
            "Workflow complete. {rows} row(s) ready for export."
        ),
        "showing_source": "Showing source data.",
        "no_processed_title": "No Processed Data",
        "no_processed_message": (
            "Apply the workflow before viewing processed data."
        ),
        "showing_processed": "Showing processed data.",
        "missing_rename_title": "Missing Rename Rule",
        "missing_rename_message": (
            "Choose a column and enter its new name."
        ),
        "save_profile_title": "Save workflow profile",
        "json_profile": "JSON profile",
        "save_error": "Save Error",
        "log_saved_profile": "Saved workflow profile: {name}",
        "profile_saved_status": "Workflow profile saved.",
        "load_profile_title": "Load workflow profile",
        "profile_error": "Profile Error",
        "log_loaded_profile": "Loaded workflow profile: {name}",
        "profile_loaded_status": (
            "Workflow profile loaded. Review and apply it."
        ),
        "export_csv_title": "Export processed CSV",
        "csv_file": "CSV file",
        "export_excel_title": "Export processed Excel workbook",
        "excel_workbook": "Excel workbook",
        "export_json_title": "Export processed JSON",
        "json_file": "JSON file",
        "export_issues_title": "Export validation report",
        "csv_report": "CSV report",
        "rules_cleared": "Workflow rules cleared.",
        "export_error": "Export Error",
        "log_exported": "Exported file: {name}",
        "export_status": "Export completed: {name}",
        "export_completed_title": "Export Completed",
        "export_completed_message": "The file was exported successfully.",
        "language_changed": "Interface language changed to English.",
        "engine_file_missing": "The selected data file does not exist.",
        "engine_unsupported_type": (
            "Unsupported file type. Choose: {supported}"
        ),
        "engine_excel_dependency": (
            "Excel support requires openpyxl. Install it with: "
            "python -m pip install -r requirements.txt"
        ),
        "engine_empty_file": "The selected file is empty.",
        "engine_no_headers": (
            "The selected file does not contain column headers."
        ),
        "engine_excel_read_error": (
            "The Excel workbook could not be read: {error}"
        ),
        "engine_no_worksheets": (
            "The Excel workbook does not contain a worksheet."
        ),
        "engine_worksheet_not_found": (
            "Worksheet not found: {sheet}. Available: {available}"
        ),
        "engine_empty_worksheet": "The selected worksheet is empty.",
        "engine_no_worksheet_headers": (
            "The selected worksheet does not contain column headers in row 1."
        ),
        "engine_load_before_process": (
            "Load a CSV, TXT, or XLSX file before processing."
        ),
        "engine_required_not_found": (
            "Required column(s) not found: {columns}"
        ),
        "engine_filter_not_found": "Filter column not found: {column}",
        "engine_missing_required": "Required value is missing.",
        "engine_apply_before_export": (
            "Apply the workflow before exporting data."
        ),
        "engine_text_read_error": "The file could not be read: {error}",
        "engine_encoding_error": "The file encoding could not be detected.",
        "engine_excel_save_error": (
            "The Excel workbook could not be saved: {error}"
        ),
        "engine_profile_load_error": (
            "The workflow profile could not be loaded: {error}"
        ),
        "engine_profile_object_error": (
            "The workflow profile must contain a JSON object."
        ),
        "summary_sheet": "Workflow Summary",
        "processed_sheet": "Processed Data",
        "issues_sheet": "Validation Issues",
        "summary_title": "Business Data Automation Studio",
        "summary_source_file": "Source file",
        "summary_source_type": "Source type",
        "summary_worksheet": "Worksheet",
        "summary_not_applicable": "Not applicable",
        "summary_source_rows": "Source rows",
        "summary_output_rows": "Output rows",
        "summary_empty_removed": "Empty rows removed",
        "summary_filtered_removed": "Filtered rows removed",
        "summary_duplicates_removed": "Duplicates removed",
        "summary_validation_issues": "Validation issues",
        "issues_source_row": "Source Row",
        "issues_column": "Column",
        "issues_message": "Message",
        "issues_value": "Value",
        "issues_none": "No validation issues found.",
    },
    "tr": {
        "app_title": "İş Verisi Otomasyon Stüdyosu",
        "app_subtitle": (
            "İş verilerini yeniden kullanılabilir iş akışı profilleriyle "
            "içe aktarın, doğrulayın, temizleyin, filtreleyin ve dışa aktarın."
        ),
        "language": "Dil:",
        "no_file": "Veri dosyası seçilmedi",
        "load_prompt": "Başlamak için CSV, TXT veya XLSX dosyası yükleyin.",
        "ready": "Hazır.",
        "select_data_file": "Veri Dosyası Seç",
        "excel_worksheet": "Excel çalışma sayfası:",
        "data_preview": "Veri Önizleme",
        "workflow_rules": "İş Akışı Kuralları",
        "export_log": "Dışa Aktarım ve Kayıt",
        "show_source": "Kaynak Veriyi Göster",
        "show_processed": "İşlenmiş Veriyi Göster",
        "cleaning_rules": "Temizleme Kuralları",
        "trim_whitespace": "Tüm hücrelerdeki fazla boşlukları temizle",
        "normalize_headers": "Sütun başlıklarını standartlaştır",
        "remove_empty": "Tamamen boş satırları kaldır",
        "remove_duplicates": "Tekrarlanan satırları kaldır",
        "validation": "Doğrulama",
        "required_columns": "Zorunlu sütunlar (virgülle ayırın):",
        "row_filter": "Satır Filtresi",
        "column": "Sütun:",
        "condition": "Koşul:",
        "value": "Değer:",
        "column_rename": "Sütun Yeniden Adlandırma",
        "current_column": "Mevcut sütun:",
        "new_name": "Yeni ad:",
        "add_rename": "Adlandırma Kuralı Ekle",
        "no_rename_rules": "Sütun adlandırma kuralı yok.",
        "apply_workflow": "İş Akışını Uygula",
        "save_profile": "İş Akışı Profilini Kaydet",
        "load_profile": "İş Akışı Profili Yükle",
        "clear_rules": "Kuralları Temizle",
        "export_processed": "İşlenmiş Veriyi Dışa Aktar",
        "export_csv": "CSV Dışa Aktar",
        "export_excel": "Excel Dışa Aktar",
        "export_json": "JSON Dışa Aktar",
        "export_validation": "Doğrulama Raporunu Dışa Aktar",
        "processing_log": "İşlem Kaydı",
        "select_data_title": "CSV, TXT veya Excel veri dosyası seçin",
        "supported_files": "Desteklenen veri dosyaları",
        "excel_workbooks": "Excel çalışma kitapları",
        "csv_files": "CSV dosyaları",
        "text_files": "Metin dosyaları",
        "all_files": "Tüm dosyalar",
        "file_error": "Dosya Hatası",
        "data_loaded_status": (
            "Veri yüklendi. İş akışı kurallarını ayarlayıp uygulayın."
        ),
        "log_loaded_file": "Veri dosyası yüklendi: {name}",
        "log_selected_sheet": "Excel çalışma sayfası seçildi: {sheet}",
        "worksheet_error": "Çalışma Sayfası Hatası",
        "worksheet_loaded_status": (
            "Çalışma sayfası yüklendi: {sheet}. İş akışı kurallarını ayarlayın."
        ),
        "file_info_excel": (
            "{rows} satır, {columns} sütun · Excel çalışma sayfası: {sheet}"
        ),
        "file_info_text": (
            "{rows} satır, {columns} sütun · "
            "Kodlama: {encoding} · Ayraç: {delimiter}"
        ),
        "delimiter_comma": "virgül",
        "delimiter_semicolon": "noktalı virgül",
        "delimiter_tab": "sekme",
        "delimiter_pipe": "dikey çizgi",
        "workflow_error": "İş Akışı Hatası",
        "log_workflow_completed": (
            "İş akışı tamamlandı: {rows} çıktı satırı, "
            "{duplicates} tekrar kaldırıldı, "
            "{issues} doğrulama sorunu bulundu."
        ),
        "workflow_complete_status": (
            "İş akışı tamamlandı. {rows} satır dışa aktarmaya hazır."
        ),
        "showing_source": "Kaynak veri gösteriliyor.",
        "no_processed_title": "İşlenmiş Veri Yok",
        "no_processed_message": (
            "İşlenmiş veriyi görüntülemeden önce iş akışını uygulayın."
        ),
        "showing_processed": "İşlenmiş veri gösteriliyor.",
        "missing_rename_title": "Adlandırma Kuralı Eksik",
        "missing_rename_message": (
            "Bir sütun seçin ve yeni adını girin."
        ),
        "save_profile_title": "İş akışı profilini kaydet",
        "json_profile": "JSON profili",
        "save_error": "Kaydetme Hatası",
        "log_saved_profile": "İş akışı profili kaydedildi: {name}",
        "profile_saved_status": "İş akışı profili kaydedildi.",
        "load_profile_title": "İş akışı profili yükle",
        "profile_error": "Profil Hatası",
        "log_loaded_profile": "İş akışı profili yüklendi: {name}",
        "profile_loaded_status": (
            "İş akışı profili yüklendi. İnceleyip uygulayın."
        ),
        "export_csv_title": "İşlenmiş CSV dosyasını dışa aktar",
        "csv_file": "CSV dosyası",
        "export_excel_title": "İşlenmiş Excel çalışma kitabını dışa aktar",
        "excel_workbook": "Excel çalışma kitabı",
        "export_json_title": "İşlenmiş JSON dosyasını dışa aktar",
        "json_file": "JSON dosyası",
        "export_issues_title": "Doğrulama raporunu dışa aktar",
        "csv_report": "CSV raporu",
        "rules_cleared": "İş akışı kuralları temizlendi.",
        "export_error": "Dışa Aktarım Hatası",
        "log_exported": "Dosya dışa aktarıldı: {name}",
        "export_status": "Dışa aktarım tamamlandı: {name}",
        "export_completed_title": "Dışa Aktarım Tamamlandı",
        "export_completed_message": "Dosya başarıyla dışa aktarıldı.",
        "language_changed": "Arayüz dili Türkçe olarak değiştirildi.",
        "engine_file_missing": "Seçilen veri dosyası bulunamadı.",
        "engine_unsupported_type": (
            "Desteklenmeyen dosya türü. Şunlardan birini seçin: {supported}"
        ),
        "engine_excel_dependency": (
            "Excel desteği için openpyxl gereklidir. Şu komutla kurun: "
            "python -m pip install -r requirements.txt"
        ),
        "engine_empty_file": "Seçilen dosya boş.",
        "engine_no_headers": "Seçilen dosyada sütun başlığı bulunamadı.",
        "engine_excel_read_error": (
            "Excel çalışma kitabı okunamadı: {error}"
        ),
        "engine_no_worksheets": (
            "Excel çalışma kitabında çalışma sayfası bulunmuyor."
        ),
        "engine_worksheet_not_found": (
            "Çalışma sayfası bulunamadı: {sheet}. Kullanılabilir: {available}"
        ),
        "engine_empty_worksheet": "Seçilen çalışma sayfası boş.",
        "engine_no_worksheet_headers": (
            "Seçilen çalışma sayfasının ilk satırında sütun başlığı bulunamadı."
        ),
        "engine_load_before_process": (
            "İşlemden önce CSV, TXT veya XLSX dosyası yükleyin."
        ),
        "engine_required_not_found": (
            "Zorunlu sütunlar bulunamadı: {columns}"
        ),
        "engine_filter_not_found": "Filtre sütunu bulunamadı: {column}",
        "engine_missing_required": "Zorunlu değer eksik.",
        "engine_apply_before_export": (
            "Veriyi dışa aktarmadan önce iş akışını uygulayın."
        ),
        "engine_text_read_error": "Dosya okunamadı: {error}",
        "engine_encoding_error": "Dosya kodlaması algılanamadı.",
        "engine_excel_save_error": (
            "Excel çalışma kitabı kaydedilemedi: {error}"
        ),
        "engine_profile_load_error": (
            "İş akışı profili yüklenemedi: {error}"
        ),
        "engine_profile_object_error": (
            "İş akışı profili bir JSON nesnesi içermelidir."
        ),
        "summary_sheet": "İş Akışı Özeti",
        "processed_sheet": "İşlenmiş Veri",
        "issues_sheet": "Doğrulama Sorunları",
        "summary_title": "İş Verisi Otomasyon Stüdyosu",
        "summary_source_file": "Kaynak dosya",
        "summary_source_type": "Kaynak türü",
        "summary_worksheet": "Çalışma sayfası",
        "summary_not_applicable": "Uygulanamaz",
        "summary_source_rows": "Kaynak satırları",
        "summary_output_rows": "Çıktı satırları",
        "summary_empty_removed": "Kaldırılan boş satırlar",
        "summary_filtered_removed": "Filtreyle kaldırılan satırlar",
        "summary_duplicates_removed": "Kaldırılan tekrarlar",
        "summary_validation_issues": "Doğrulama sorunları",
        "issues_source_row": "Kaynak Satır",
        "issues_column": "Sütun",
        "issues_message": "Mesaj",
        "issues_value": "Değer",
        "issues_none": "Doğrulama sorunu bulunamadı.",
    },
}


def detect_default_language() -> str:
    """Use Turkish on Turkish systems and English everywhere else."""
    try:
        locale_name = locale.getlocale()[0] or ""
    except (ValueError, TypeError):
        locale_name = ""
    return "tr" if locale_name.lower().startswith("tr") else "en"


def language_label(language: str) -> str:
    for label, code in LANGUAGE_LABELS.items():
        if code == language:
            return label
    return "English"


def translate(language: str, key: str, **values) -> str:
    selected = language if language in TRANSLATIONS else "en"
    template = TRANSLATIONS[selected].get(key, TRANSLATIONS["en"].get(key, key))
    return template.format(**values)


def filter_label(language: str, mode: str) -> str:
    selected = language if language in FILTER_MODE_LABELS else "en"
    return FILTER_MODE_LABELS[selected].get(mode, mode)


def filter_mode_from_label(language: str, label: str) -> str:
    selected = language if language in FILTER_MODE_LABELS else "en"
    for mode, translated_label in FILTER_MODE_LABELS[selected].items():
        if translated_label == label:
            return mode
    return "contains"
