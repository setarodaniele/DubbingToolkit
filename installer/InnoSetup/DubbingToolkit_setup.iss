[Setup]
AppName=Dubbing Toolkit
AppId={{A367F698-E94A-4726-BC26-C48F895E69D7}
AppVersion=0.1
DefaultDirName=C:\DubbingToolkit
DefaultGroupName=Dubbing Toolkit
OutputDir=output
OutputBaseFilename=setup_dubbing_toolkit
Compression=none
SolidCompression=no
SetupIconFile=assets\DubbingToolkit_Studio.ico
UninstallDisplayIcon={app}\assets\DubbingToolkit_Studio.ico
ShowLanguageDialog=auto

; ============================================================
; [01] LINGUE
; ============================================================
[Languages]
Name: "english";    MessagesFile: "compiler:Default.isl"
Name: "italian";    MessagesFile: "compiler:Languages\Italian.isl"
Name: "french";     MessagesFile: "compiler:Languages\French.isl"
Name: "german";     MessagesFile: "compiler:Languages\German.isl"
Name: "spanish";    MessagesFile: "compiler:Languages\Spanish.isl"
Name: "portuguese"; MessagesFile: "compiler:Languages\Portuguese.isl"
Name: "dutch";      MessagesFile: "compiler:Languages\Dutch.isl"
Name: "polish";     MessagesFile: "compiler:Languages\Polish.isl"
Name: "russian";    MessagesFile: "compiler:Languages\Russian.isl"
Name: "japanese";   MessagesFile: "compiler:Languages\Japanese.isl"

; ============================================================
; [02] MESSAGGI PERSONALIZZATI
; ============================================================
[CustomMessages]

; --- [02.01] CARTELLA PROGRAMMI ---
english.NoProgramFiles=Dubbing Toolkit requires write access to its folder during execution.%n%nThe "Program Files" folder is not compatible with this requirement.%n%nRecommended path: C:\DubbingToolkit
italian.NoProgramFiles=Dubbing Toolkit richiede accesso in scrittura alla propria cartella durante l'esecuzione.%n%nLa cartella "Programmi" non è compatibile con questo requisito.%n%nPercorso consigliato: C:\DubbingToolkit
french.NoProgramFiles=Dubbing Toolkit nécessite un accès en écriture à son dossier pendant l'exécution.%n%nLe dossier "Programmes" n'est pas compatible avec cette exigence.%n%nChemin recommandé : C:\DubbingToolkit
german.NoProgramFiles=Dubbing Toolkit benötigt während der Ausführung Schreibzugriff auf seinen Ordner.%n%nDer Ordner "Programme" ist mit dieser Anforderung nicht kompatibel.%n%nEmpfohlener Pfad: C:\DubbingToolkit
spanish.NoProgramFiles=Dubbing Toolkit requiere acceso de escritura a su carpeta durante la ejecución.%n%nLa carpeta "Archivos de programa" no es compatible con este requisito.%n%nRuta recomendada: C:\DubbingToolkit
portuguese.NoProgramFiles=O Dubbing Toolkit requer acesso de gravação à sua pasta durante a execução.%n%nA pasta "Arquivos de Programas" não é compatível com este requisito.%n%nCaminho recomendado: C:\DubbingToolkit
dutch.NoProgramFiles=Dubbing Toolkit vereist schrijftoegang tot zijn map tijdens uitvoering.%n%nDe map "Programmabestanden" is niet compatibel met deze vereiste.%n%nAanbevolen pad: C:\DubbingToolkit
polish.NoProgramFiles=Dubbing Toolkit wymaga dostępu do zapisu do swojego folderu podczas działania.%n%nFolder "Program Files" nie jest zgodny z tym wymaganiem.%n%nZalecana ścieżka: C:\DubbingToolkit
russian.NoProgramFiles=Dubbing Toolkit требует доступа для записи в свою папку во время работы.%n%nПапка "Program Files" не совместима с этим требованием.%n%nРекомендуемый путь: C:\DubbingToolkit
japanese.NoProgramFiles=Dubbing Toolkit は実行中にフォルダへの書き込みアクセスが必要です。%n%n"Program Files" フォルダはこの要件と互換性がありません。%n%n推奨パス: C:\DubbingToolkit

; --- [02.02] PRONTO PER INSTALLAZIONE / AGGIORNAMENTO ---
english.ReadyToInstall=The program is ready to install.
english.ReadyToUpdate=A previous version was detected. The program is ready to update.
italian.ReadyToInstall=Il programma è pronto per l'installazione.
italian.ReadyToUpdate=È stata rilevata una versione precedente. Il programma è pronto per l'aggiornamento.
french.ReadyToInstall=Le programme est prêt à être installé.
french.ReadyToUpdate=Une version précédente a été détectée. Le programme est prêt à être mis à jour.
german.ReadyToInstall=Das Programm ist zur Installation bereit.
german.ReadyToUpdate=Eine frühere Version wurde gefunden. Das Programm ist bereit für die Aktualisierung.
spanish.ReadyToInstall=El programa está listo para instalarse.
spanish.ReadyToUpdate=Se detectó una versión anterior. El programa está listo para actualizarse.
portuguese.ReadyToInstall=O programa está pronto para ser instalado.
portuguese.ReadyToUpdate=Uma versão anterior foi detectada. O programa está pronto para ser atualizado.
dutch.ReadyToInstall=Het programma is klaar om te installeren.
dutch.ReadyToUpdate=Een eerdere versie is gevonden. Het programma is klaar om bij te werken.
polish.ReadyToInstall=Program jest gotowy do instalacji.
polish.ReadyToUpdate=Wykryto poprzednią wersję. Program jest gotowy do aktualizacji.
russian.ReadyToInstall=Программа готова к установке.
russian.ReadyToUpdate=Обнаружена предыдущая версия. Программа готова к обновлению.
japanese.ReadyToInstall=プログラムはインストールの準備ができています。
japanese.ReadyToUpdate=以前のバージョンが検出されました。プログラムはアップデートの準備ができています。

; --- [02.03] DIALOG DISINSTALLAZIONE CHECKBOX ---
english.UninstallDataTitle=Data removal options
english.UninstallDataMsg=Select what you want to permanently delete:
english.UninstallCredentials=Credentials and API keys (credentials folder)
english.UninstallBilling=Billing data - monthly TTS usage log (Billing folder)
italian.UninstallDataTitle=Opzioni di rimozione dati
italian.UninstallDataMsg=Seleziona cosa vuoi eliminare definitivamente:
italian.UninstallCredentials=Credenziali e chiavi API (cartella credentials)
italian.UninstallBilling=Dati di fatturazione - log consumo TTS mensile (cartella Billing)
french.UninstallDataTitle=Options de suppression des données
french.UninstallDataMsg=Sélectionnez ce que vous souhaitez supprimer définitivement :
french.UninstallCredentials=Identifiants et clés API (dossier credentials)
french.UninstallBilling=Données de facturation - journal d'utilisation TTS mensuel (dossier Billing)
german.UninstallDataTitle=Optionen zur Datenlöschung
german.UninstallDataMsg=Wählen Sie aus, was Sie dauerhaft löschen möchten:
german.UninstallCredentials=Anmeldedaten und API-Schlüssel (Ordner credentials)
german.UninstallBilling=Abrechnungsdaten - monatliches TTS-Nutzungsprotokoll (Ordner Billing)
spanish.UninstallDataTitle=Opciones de eliminación de datos
spanish.UninstallDataMsg=Seleccione qué desea eliminar de forma permanente:
spanish.UninstallCredentials=Credenciales y claves API (carpeta credentials)
spanish.UninstallBilling=Datos de facturación - registro de uso TTS mensual (carpeta Billing)
portuguese.UninstallDataTitle=Opções de remoção de dados
portuguese.UninstallDataMsg=Selecione o que deseja excluir permanentemente:
portuguese.UninstallCredentials=Credenciais e chaves de API (pasta credentials)
portuguese.UninstallBilling=Dados de faturamento - log de uso TTS mensal (pasta Billing)
dutch.UninstallDataTitle=Opties voor gegevensverwijdering
dutch.UninstallDataMsg=Selecteer wat u permanent wilt verwijderen:
dutch.UninstallCredentials=Inloggegevens en API-sleutels (map credentials)
dutch.UninstallBilling=Factureringsgegevens - maandelijks TTS-gebruikslogboek (map Billing)
polish.UninstallDataTitle=Opcje usuwania danych
polish.UninstallDataMsg=Wybierz, co chcesz trwale usunąć:
polish.UninstallCredentials=Dane uwierzytelniające i klucze API (folder credentials)
polish.UninstallBilling=Dane rozliczeniowe - miesięczny dziennik użycia TTS (folder Billing)
russian.UninstallDataTitle=Параметры удаления данных
russian.UninstallDataMsg=Выберите, что вы хотите удалить навсегда:
russian.UninstallCredentials=Учётные данные и ключи API (папка credentials)
russian.UninstallBilling=Данные о выставлении счетов - журнал использования TTS (папка Billing)
japanese.UninstallDataTitle=データ削除オプション
japanese.UninstallDataMsg=完全に削除するものを選択してください：
japanese.UninstallCredentials=認証情報と API キー（credentials フォルダ）
japanese.UninstallBilling=請求データ - 月次 TTS 使用ログ（Billing フォルダ）

; --- [02.04] MESSAGGIO FINALE DISINSTALLAZIONE ---
english.UninstallRemainingMsg=If work files were present, the following folders may have been preserved:%n%n  - Audio_Extracted%n  - Audio_Input%n  - Billing%n  - credentials%n  - Dubbed%n  - Logs%n  - Output%n  - Transcripts%n  - Translated%n  - Video_Input%n%nIf present, you can find them in the installation folder and delete them manually if you no longer need them.
italian.UninstallRemainingMsg=Se erano presenti file di lavoro, le seguenti cartelle potrebbero essere state preservate:%n%n  - Audio_Extracted%n  - Audio_Input%n  - Billing%n  - credentials%n  - Dubbed%n  - Logs%n  - Output%n  - Transcripts%n  - Translated%n  - Video_Input%n%nSe presenti, le trovi nella cartella di installazione. Puoi eliminarle manualmente se non ti servono più.
french.UninstallRemainingMsg=Si des fichiers de travail étaient présents, les dossiers suivants ont peut-être été conservés :%n%n  - Audio_Extracted%n  - Audio_Input%n  - Billing%n  - credentials%n  - Dubbed%n  - Logs%n  - Output%n  - Transcripts%n  - Translated%n  - Video_Input%n%nS'ils sont présents, vous les trouverez dans le dossier d'installation. Vous pouvez les supprimer manuellement si vous n'en avez plus besoin.
german.UninstallRemainingMsg=Wenn Arbeitsdateien vorhanden waren, wurden die folgenden Ordner möglicherweise beibehalten:%n%n  - Audio_Extracted%n  - Audio_Input%n  - Billing%n  - credentials%n  - Dubbed%n  - Logs%n  - Output%n  - Transcripts%n  - Translated%n  - Video_Input%n%nFalls vorhanden, finden Sie sie im Installationsordner. Sie können sie manuell löschen, wenn Sie sie nicht mehr benötigen.
spanish.UninstallRemainingMsg=Si había archivos de trabajo presentes, es posible que se hayan conservado las siguientes carpetas:%n%n  - Audio_Extracted%n  - Audio_Input%n  - Billing%n  - credentials%n  - Dubbed%n  - Logs%n  - Output%n  - Transcripts%n  - Translated%n  - Video_Input%n%nSi están presentes, puede encontrarlas en la carpeta de instalación. Puede eliminarlas manualmente si ya no las necesita.
portuguese.UninstallRemainingMsg=Se havia arquivos de trabalho presentes, as seguintes pastas podem ter sido preservadas:%n%n  - Audio_Extracted%n  - Audio_Input%n  - Billing%n  - credentials%n  - Dubbed%n  - Logs%n  - Output%n  - Transcripts%n  - Translated%n  - Video_Input%n%nSe presentes, você pode encontrá-las na pasta de instalação. Pode excluí-las manualmente se não precisar mais delas.
dutch.UninstallRemainingMsg=Als er werkbestanden aanwezig waren, zijn de volgende mappen mogelijk bewaard:%n%n  - Audio_Extracted%n  - Audio_Input%n  - Billing%n  - credentials%n  - Dubbed%n  - Logs%n  - Output%n  - Transcripts%n  - Translated%n  - Video_Input%n%nAls ze aanwezig zijn, kunt u ze vinden in de installatiemap. U kunt ze handmatig verwijderen als u ze niet meer nodig heeft.
polish.UninstallRemainingMsg=Jeśli były obecne pliki robocze, następujące foldery mogły zostać zachowane:%n%n  - Audio_Extracted%n  - Audio_Input%n  - Billing%n  - credentials%n  - Dubbed%n  - Logs%n  - Output%n  - Transcripts%n  - Translated%n  - Video_Input%n%nJeśli są obecne, znajdziesz je w folderze instalacyjnym. Możesz je ręcznie usunąć, jeśli nie są już potrzebne.
russian.UninstallRemainingMsg=Если рабочие файлы присутствовали, следующие папки могли быть сохранены:%n%n  - Audio_Extracted%n  - Audio_Input%n  - Billing%n  - credentials%n  - Dubbed%n  - Logs%n  - Output%n  - Transcripts%n  - Translated%n  - Video_Input%n%nЕсли они присутствуют, вы найдёте их в папке установки. Вы можете удалить их вручную, если они вам больше не нужны.
japanese.UninstallRemainingMsg=作業ファイルが存在した場合、以下のフォルダが保存されている可能性があります：%n%n  - Audio_Extracted%n  - Audio_Input%n  - Billing%n  - credentials%n  - Dubbed%n  - Logs%n  - Output%n  - Transcripts%n  - Translated%n  - Video_Input%n%n存在する場合は、インストールフォルダ内にあります。不要であれば手動で削除できます。

; ============================================================
; [03] FILE
; ============================================================
[Files]
Source: "..\build_payload\core\*";                       DestDir: "{app}\core";        Flags: recursesubdirs createallsubdirs ignoreversion
Source: "..\build_payload\locale\*";                     DestDir: "{app}\locale";      Flags: recursesubdirs createallsubdirs ignoreversion
Source: "..\build_payload\ps\*";                         DestDir: "{app}\ps";          Flags: recursesubdirs createallsubdirs ignoreversion
Source: "..\build_payload\Scripts\*";                    DestDir: "{app}\Scripts";     Flags: recursesubdirs createallsubdirs ignoreversion
Source: "..\build_payload\Settings\*";                   DestDir: "{app}\Settings";    Flags: recursesubdirs createallsubdirs ignoreversion
Source: "..\build_payload\Docs\*";                       DestDir: "{app}\Docs";        Flags: recursesubdirs createallsubdirs ignoreversion
Source: "..\build_payload\Billing\tts_voices_cost.json"; DestDir: "{app}\Billing";     Flags: ignoreversion
Source: "..\build_payload\credentials\*";                DestDir: "{app}\credentials"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "..\build_payload\StartDubbing.bat";             DestDir: "{app}";             Flags: ignoreversion
Source: "assets\DubbingToolkit_Studio.ico";              DestDir: "{app}\assets";      Flags: ignoreversion
Source: "assets\DubbingToolkit_Workspace.ico";           DestDir: "{app}\assets";      Flags: ignoreversion

; ============================================================
; [04] CARTELLE DATI UTENTE
; ============================================================
[Dirs]
Name: "{app}\Audio_Input"
Name: "{app}\Audio_Extracted"
Name: "{app}\Dubbed"
Name: "{app}\Output"
Name: "{app}\Transcripts"
Name: "{app}\Translated"
Name: "{app}\Video_Input"
Name: "{app}\Logs"
Name: "{app}\Workspace"

; ============================================================
; [05] SHORTCUT
; ============================================================
[Icons]
Name: "{commondesktop}\Dubbing Toolkit";             Filename: "{app}\StartDubbing.bat"; IconFilename: "{app}\assets\DubbingToolkit_Studio.ico"
Name: "{commondesktop}\Dubbing Toolkit - Workspace"; Filename: "{app}\Workspace";        IconFilename: "{app}\assets\DubbingToolkit_Workspace.ico"
Name: "{group}\Dubbing Toolkit";                     Filename: "{app}\StartDubbing.bat"; IconFilename: "{app}\assets\DubbingToolkit_Studio.ico"

Name: "{app}\Workspace\Audio Input";     Filename: "{app}\Audio_Input";     IconFilename: "{app}\assets\DubbingToolkit_Workspace.ico"
Name: "{app}\Workspace\Audio Extracted"; Filename: "{app}\Audio_Extracted"; IconFilename: "{app}\assets\DubbingToolkit_Workspace.ico"
Name: "{app}\Workspace\Dubbed";          Filename: "{app}\Dubbed";          IconFilename: "{app}\assets\DubbingToolkit_Workspace.ico"
Name: "{app}\Workspace\Transcripts";     Filename: "{app}\Transcripts";     IconFilename: "{app}\assets\DubbingToolkit_Workspace.ico"
Name: "{app}\Workspace\Translated";      Filename: "{app}\Translated";      IconFilename: "{app}\assets\DubbingToolkit_Workspace.ico"

; ============================================================
; [06] ELIMINAZIONE IN DISINSTALLAZIONE
; ============================================================
[UninstallDelete]
Type: filesandordirs; Name: "{app}\core"
Type: filesandordirs; Name: "{app}\locale"
Type: filesandordirs; Name: "{app}\ps"
Type: filesandordirs; Name: "{app}\Scripts"
Type: filesandordirs; Name: "{app}\Settings"
Type: filesandordirs; Name: "{app}\assets"
Type: filesandordirs; Name: "{app}\Docs"
Type: filesandordirs; Name: "{app}\Tools"
Type: filesandordirs; Name: "{app}\voices"
Type: filesandordirs; Name: "{app}\Installation"
Type: filesandordirs; Name: "{app}\Workspace"
Type: files;          Name: "{app}\StartDubbing.bat"


; ============================================================
; [07] AVVIO POST-INSTALLAZIONE
; ============================================================
[Run]
Filename: "{app}\StartDubbing.bat"; Description: "Avvia Dubbing Toolkit"; Flags: nowait postinstall

; ============================================================
; [08] CODICE PASCAL
; ============================================================
[Code]

// ------------------------------------------------------------
// [08.01] VARIABILI GLOBALI
// ------------------------------------------------------------
var
  DeleteCredentials: Boolean;
  DeleteBilling:     Boolean;
  IsUpgrade:         Boolean;

// ------------------------------------------------------------
// [08.02] FORM CHECKBOX DISINSTALLAZIONE
// ------------------------------------------------------------
procedure ShowUninstallOptionsForm;
var
  Form:       TForm;
  LblTitle:   TLabel;
  LblMsg:     TLabel;
  ChkCred:    TCheckBox;
  ChkBilling: TCheckBox;
  BtnOK:      TButton;
begin
  DeleteCredentials := False;
  DeleteBilling     := False;

  Form := TForm.Create(nil);
  Form.Caption      := CustomMessage('UninstallDataTitle');
  Form.ClientWidth  := 480;
  Form.ClientHeight := 220;
  Form.Position     := poScreenCenter;
  Form.BorderStyle  := bsDialog;

  LblTitle := TLabel.Create(Form);
  LblTitle.Parent     := Form;
  LblTitle.Left       := 20;
  LblTitle.Top        := 20;
  LblTitle.Width      := 440;
  LblTitle.Caption    := CustomMessage('UninstallDataTitle');
  LblTitle.Font.Style := [fsBold];

  LblMsg := TLabel.Create(Form);
  LblMsg.Parent  := Form;
  LblMsg.Left    := 20;
  LblMsg.Top     := 50;
  LblMsg.Width   := 440;
  LblMsg.Caption := CustomMessage('UninstallDataMsg');

  ChkCred := TCheckBox.Create(Form);
  ChkCred.Parent  := Form;
  ChkCred.Left    := 20;
  ChkCred.Top     := 80;
  ChkCred.Width   := 440;
  ChkCred.Caption := CustomMessage('UninstallCredentials');
  ChkCred.Checked := False;

  ChkBilling := TCheckBox.Create(Form);
  ChkBilling.Parent  := Form;
  ChkBilling.Left    := 20;
  ChkBilling.Top     := 110;
  ChkBilling.Width   := 440;
  ChkBilling.Caption := CustomMessage('UninstallBilling');
  ChkBilling.Checked := False;

  BtnOK := TButton.Create(Form);
  BtnOK.Parent      := Form;
  BtnOK.Caption     := 'OK';
  BtnOK.Left        := 195;
  BtnOK.Top         := 165;
  BtnOK.Width       := 90;
  BtnOK.ModalResult := mrOK;

  Form.ShowModal;

  DeleteCredentials := ChkCred.Checked;
  DeleteBilling     := ChkBilling.Checked;

  Form.Free;
end;

// ------------------------------------------------------------
// [08.03] PULIZIA CARTELLE APP (aggiornamento)
// ------------------------------------------------------------
procedure CleanAppFolders(InstallDir: String);
var
  AppFolders: TStringList;
  i:          Integer;
  FolderPath: String;
begin
  AppFolders := TStringList.Create;
  try
    AppFolders.Add('core');
    AppFolders.Add('locale');
    AppFolders.Add('ps');
    AppFolders.Add('Scripts');
    AppFolders.Add('Settings');
    AppFolders.Add('assets');
    AppFolders.Add('Docs');
    AppFolders.Add('Tools');
    AppFolders.Add('voices');
    AppFolders.Add('Installation');

    for i := 0 to AppFolders.Count - 1 do
    begin
      FolderPath := InstallDir + '\' + AppFolders[i];
      if DirExists(FolderPath) then
        DelTree(FolderPath, True, True, True);
    end;
  finally
    AppFolders.Free;
  end;
end;

// ------------------------------------------------------------
// [08.04] INIZIALIZZAZIONE WIZARD
// ------------------------------------------------------------
procedure InitializeWizard();
var
  RegKey:          String;
  ExistingVersion: String;
begin
  IsUpgrade := False;
  RegKey := 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\' +
            '{A367F698-E94A-4726-BC26-C48F895E69D7}' + '_is1';

  if RegQueryStringValue(HKLM, RegKey, 'DisplayVersion', ExistingVersion) or
     RegQueryStringValue(HKCU, RegKey, 'DisplayVersion', ExistingVersion) or
     RegQueryStringValue(HKLM64, RegKey, 'DisplayVersion', ExistingVersion) then
  begin
    IsUpgrade := True;
    MsgBox(CustomMessage('ReadyToUpdate'), mbInformation, MB_OK);
  end;
end;

// ------------------------------------------------------------
// [08.05] CAMBIO PAGINA WIZARD
// ------------------------------------------------------------
procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpReady then
  begin
    WizardForm.ReadyMemo.Lines.Clear;
    if IsUpgrade then
      WizardForm.ReadyMemo.Lines.Add(CustomMessage('ReadyToUpdate'))
    else
      WizardForm.ReadyMemo.Lines.Add(CustomMessage('ReadyToInstall'));
  end;
end;

// ------------------------------------------------------------
// [08.06] BLOCCO CARTELLA PROGRAMMI
// ------------------------------------------------------------
function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  if CurPageID = wpSelectDir then
  begin
    if Pos('\program files', Lowercase(WizardDirValue)) > 0 then
    begin
      MsgBox(CustomMessage('NoProgramFiles'), mbError, MB_OK);
      Result := False;
    end;
  end;
end;

// ------------------------------------------------------------
// [08.07] PULIZIA PRE-INSTALLAZIONE
// ------------------------------------------------------------
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssInstall then
  begin
    if DirExists(WizardDirValue) then
      CleanAppFolders(WizardDirValue);
  end;
end;

// ------------------------------------------------------------
// [08.08] DISINSTALLAZIONE
// ------------------------------------------------------------
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usUninstall then
  begin
    ShowUninstallOptionsForm;

    if DeleteCredentials then
      if DirExists(ExpandConstant('{app}\credentials')) then
        DelTree(ExpandConstant('{app}\credentials'), True, True, True);

    if DeleteBilling then
    begin
      if DirExists(ExpandConstant('{app}\Billing')) then
        DelTree(ExpandConstant('{app}\Billing'), True, True, True);
    end else begin
      if FileExists(ExpandConstant('{app}\Billing\tts_voices_cost.json')) then
        DeleteFile(ExpandConstant('{app}\Billing\tts_voices_cost.json'));
    end;
  end;

  if CurUninstallStep = usPostUninstall then
    MsgBox(CustomMessage('UninstallRemainingMsg'), mbInformation, MB_OK);
end;