[Setup]
AppName=Dubbing Toolkit
AppId={{A367F698-E94A-4726-BC26-C48F895E69D7}
AppVersion=0.1
DefaultDirName=C:\DubbingToolkit
DefaultGroupName=Dubbing Toolkit
OutputDir=output
OutputBaseFilename=setup_dubbing_toolkit
Compression=lzma
SolidCompression=yes
SetupIconFile=assets\DubbingToolkit_Studio.ico
UninstallDisplayIcon={app}\assets\DubbingToolkit_Studio.ico
ShowLanguageDialog=yes

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
Name: "russian";    MessagesFile: "compiler:Languages\Russian.isl"

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
russian.NoProgramFiles=Dubbing Toolkit требует доступа для записи в свою папку во время работы.%n%nПапка "Program Files" не совместима с этим требованием.%n%nРекомендуемый путь: C:\DubbingToolkit

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
russian.ReadyToInstall=Программа готова к установке.
russian.ReadyToUpdate=Обнаружена предыдущая версия. Программа готова к обновлению.

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
russian.UninstallDataTitle=Параметры удаления данных
russian.UninstallDataMsg=Выберите, что вы хотите удалить навсегда:
russian.UninstallCredentials=Учётные данные и ключи API (папка credentials)
russian.UninstallBilling=Данные о выставлении счетов - журнал использования TTS (папка Billing)

; --- [02.05] AVVISO, LAVORO E CONFERMA DISINSTALLAZIONE ---
english.UninstallWarning=WARNING: selected items will be permanently deleted.
english.UninstallWorkFiles=Work files (audio, video, transcripts, etc.)
english.UninstallConfirmMsg=Are you sure you want to permanently delete the selected items?
italian.UninstallWarning=ATTENZIONE: i dati selezionati verranno eliminati definitivamente.
italian.UninstallWorkFiles=File di lavoro (audio, video, trascrizioni, ecc.)
italian.UninstallConfirmMsg=Sei sicuro di voler eliminare definitivamente gli elementi selezionati?
french.UninstallWarning=ATTENTION : les éléments sélectionnés seront supprimés définitivement.
french.UninstallWorkFiles=Fichiers de travail (audio, vidéo, transcriptions, etc.)
french.UninstallConfirmMsg=Êtes-vous sûr de vouloir supprimer définitivement les éléments sélectionnés ?
german.UninstallWarning=WARNUNG: Die ausgewählten Elemente werden dauerhaft gelöscht.
german.UninstallWorkFiles=Arbeitsdateien (Audio, Video, Transkripte, usw.)
german.UninstallConfirmMsg=Sind Sie sicher, dass Sie die ausgewählten Elemente dauerhaft löschen möchten?
spanish.UninstallWarning=ADVERTENCIA: los elementos seleccionados se eliminarán permanentemente.
spanish.UninstallWorkFiles=Archivos de trabajo (audio, vídeo, transcripciones, etc.)
spanish.UninstallConfirmMsg=¿Está seguro de que desea eliminar permanentemente los elementos seleccionados?
portuguese.UninstallWarning=AVISO: os itens selecionados serão excluídos permanentemente.
portuguese.UninstallWorkFiles=Arquivos de trabalho (áudio, vídeo, transcrições, etc.)
portuguese.UninstallConfirmMsg=Tem certeza de que deseja excluir permanentemente os itens selecionados?
russian.UninstallWarning=ВНИМАНИЕ: выбранные элементы будут удалены безвозвратно.
russian.UninstallWorkFiles=Рабочие файлы (аудио, видео, транскрипции и др.)
russian.UninstallConfirmMsg=Вы уверены, что хотите безвозвратно удалить выбранные элементы?

; --- [02.04] MESSAGGIO FINALE DISINSTALLAZIONE ---
english.UninstallRemainingMsg=If work files were present, the following folders may have been preserved:%n%n  - Audio_Extracted%n  - Audio_Input%n  - Billing%n  - credentials%n  - Dubbed%n  - Logs%n  - Output%n  - Transcripts%n  - Translated%n  - Video_Input%n%nIf present, you can find them in the installation folder and delete them manually if you no longer need them.
italian.UninstallRemainingMsg=Se erano presenti file di lavoro, le seguenti cartelle potrebbero essere state preservate:%n%n  - Audio_Extracted%n  - Audio_Input%n  - Billing%n  - credentials%n  - Dubbed%n  - Logs%n  - Output%n  - Transcripts%n  - Translated%n  - Video_Input%n%nSe presenti, le trovi nella cartella di installazione. Puoi eliminarle manualmente se non ti servono più.
french.UninstallRemainingMsg=Si des fichiers de travail étaient présents, les dossiers suivants ont peut-être été conservés :%n%n  - Audio_Extracted%n  - Audio_Input%n  - Billing%n  - credentials%n  - Dubbed%n  - Logs%n  - Output%n  - Transcripts%n  - Translated%n  - Video_Input%n%nS'ils sont présents, vous les trouverez dans le dossier d'installation. Vous pouvez les supprimer manuellement si vous n'en avez plus besoin.
german.UninstallRemainingMsg=Wenn Arbeitsdateien vorhanden waren, wurden die folgenden Ordner möglicherweise beibehalten:%n%n  - Audio_Extracted%n  - Audio_Input%n  - Billing%n  - credentials%n  - Dubbed%n  - Logs%n  - Output%n  - Transcripts%n  - Translated%n  - Video_Input%n%nFalls vorhanden, finden Sie sie im Installationsordner. Sie können sie manuell löschen, wenn Sie sie nicht mehr benötigen.
spanish.UninstallRemainingMsg=Si había archivos de trabajo presentes, es posible que se hayan conservado las siguientes carpetas:%n%n  - Audio_Extracted%n  - Audio_Input%n  - Billing%n  - credentials%n  - Dubbed%n  - Logs%n  - Output%n  - Transcripts%n  - Translated%n  - Video_Input%n%nSi están presentes, puede encontrarlas en la carpeta de instalación. Puede eliminarlas manualmente si ya no las necesita.
portuguese.UninstallRemainingMsg=Se havia arquivos de trabalho presentes, as seguintes pastas podem ter sido preservadas:%n%n  - Audio_Extracted%n  - Audio_Input%n  - Billing%n  - credentials%n  - Dubbed%n  - Logs%n  - Output%n  - Transcripts%n  - Translated%n  - Video_Input%n%nSe presentes, você pode encontrá-las na pasta de instalação. Pode excluí-las manualmente se não precisar mais delas.
russian.UninstallRemainingMsg=Если рабочие файлы присутствовали, следующие папки могли быть сохранены:%n%n  - Audio_Extracted%n  - Audio_Input%n  - Billing%n  - credentials%n  - Dubbed%n  - Logs%n  - Output%n  - Transcripts%n  - Translated%n  - Video_Input%n%nЕсли они присутствуют, вы найдёте их в папке установки. Вы можете удалить их вручную, если они вам больше не нужны.

; ============================================================
; [03] PAYLOAD (generato automaticamente da build_manifest.ps1)
; ============================================================
#include "payload_sections.iss"

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
  DeleteWorkFiles:   Boolean;
  IsUpgrade:         Boolean;

// ------------------------------------------------------------
// [08.02] FORM CHECKBOX DISINSTALLAZIONE
// ------------------------------------------------------------
procedure ShowUninstallOptionsForm;
var
  Form:       TForm;
  LblWarning: TLabel;
  LblMsg:     TLabel;
  ChkCred:    TCheckBox;
  ChkBilling: TCheckBox;
  ChkWork:    TCheckBox;
  BtnOK:      TButton;
  Confirmed:  Boolean;
begin
  DeleteCredentials := False;
  DeleteBilling     := False;
  DeleteWorkFiles   := False;

  repeat
    Confirmed := True;

    Form := TForm.Create(nil);
    Form.Caption      := CustomMessage('UninstallDataTitle');
    Form.ClientWidth  := 480;
    Form.ClientHeight := 380;
    Form.Position     := poScreenCenter;
    Form.BorderStyle  := bsDialog;

    LblWarning := TLabel.Create(Form);
    LblWarning.Parent     := Form;
    LblWarning.AutoSize   := False;
    LblWarning.Left       := 20;
    LblWarning.Top        := 20;
    LblWarning.Width      := 440;
    LblWarning.Height     := 40;
    LblWarning.WordWrap   := True;
    LblWarning.Caption    := CustomMessage('UninstallWarning');
    LblWarning.Font.Style := [fsBold];
    LblWarning.Font.Color := clRed;

    LblMsg := TLabel.Create(Form);
    LblMsg.Parent  := Form;
    LblMsg.Left    := 20;
    LblMsg.Top     := 110;
    LblMsg.Width   := 440;
    LblMsg.Caption := CustomMessage('UninstallDataMsg');

    ChkCred := TCheckBox.Create(Form);
    ChkCred.Parent  := Form;
    ChkCred.Left    := 20;
    ChkCred.Top     := 140;
    ChkCred.Width   := 440;
    ChkCred.Caption := CustomMessage('UninstallCredentials');
    ChkCred.Checked := DeleteCredentials;

    ChkBilling := TCheckBox.Create(Form);
    ChkBilling.Parent  := Form;
    ChkBilling.Left    := 20;
    ChkBilling.Top     := 170;
    ChkBilling.Width   := 440;
    ChkBilling.Caption := CustomMessage('UninstallBilling');
    ChkBilling.Checked := DeleteBilling;

    ChkWork := TCheckBox.Create(Form);
    ChkWork.Parent  := Form;
    ChkWork.Left    := 20;
    ChkWork.Top     := 200;
    ChkWork.Width   := 440;
    ChkWork.Caption := CustomMessage('UninstallWorkFiles');
    ChkWork.Checked := DeleteWorkFiles;

    BtnOK := TButton.Create(Form);
    BtnOK.Parent      := Form;
    BtnOK.Caption     := 'OK';
    BtnOK.Left        := 195;
    BtnOK.Top         := 330;
    BtnOK.Width       := 90;
    BtnOK.ModalResult := mrOK;

    Form.ShowModal;

    DeleteCredentials := ChkCred.Checked;
    DeleteBilling     := ChkBilling.Checked;
    DeleteWorkFiles   := ChkWork.Checked;

    Form.Free;

    if DeleteCredentials or DeleteBilling or DeleteWorkFiles then
    begin
      if MsgBox(CustomMessage('UninstallConfirmMsg'), mbConfirmation, MB_YESNO) = IDNO then
        Confirmed := False;
    end;
  until Confirmed;
end;

// ------------------------------------------------------------
// [08.03] PULIZIA CARTELLE APP (aggiornamento)
// ------------------------------------------------------------
procedure FillAppFolders(AppFolders: TStringList);
begin
// ##CLEANUP_BEGIN##
  AppFolders.Add('Installation');
  AppFolders.Add('Tools');
  AppFolders.Add('core');
  AppFolders.Add('locale');
  AppFolders.Add('ps');
  AppFolders.Add('Scripts');
  AppFolders.Add('Settings');
  AppFolders.Add('Docs');
  AppFolders.Add('Workspace');
// ##CLEANUP_END##
end;

procedure CleanAppFolders(InstallDir: String);
var
  AppFolders: TStringList;
  i:          Integer;
  FolderPath: String;
begin
  AppFolders := TStringList.Create;
  try
    FillAppFolders(AppFolders);
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
// [08.07] LINGUA INSTALLER → CODICE LINGUA APP
// ------------------------------------------------------------
function GetLangCode: String;
var
  Lang: String;
begin
  Lang := ActiveLanguage;
  if      Lang = 'italian'    then Result := 'it'
  else if Lang = 'french'     then Result := 'fr'
  else if Lang = 'german'     then Result := 'de'
  else if Lang = 'spanish'    then Result := 'es'
  else if Lang = 'portuguese' then Result := 'pt'
  else if Lang = 'russian'    then Result := 'ru'
  else Result := 'en';
end;

// ------------------------------------------------------------
// [08.08] SCRITTURA SETTINGS_PERSISTENT POST-INSTALL
// ------------------------------------------------------------
// Writes a minimal settings_persistent.json so that Launcher.ps1
// skips the interactive language menu on first launch.
// BootstrapSettings.py fills the remaining fields via merge on startup.
procedure WritePersistentSettings(InstallDir: String; LangCode: String);
var
  Path:    String;
  Content: String;
begin
  Path := InstallDir + '\Settings\settings_persistent.json';
  Content :=
    '{' + #10 +
    '  "language_preset_from_installer": true,' + #10 +
    '  "interface_lang": "' + LangCode + '"' + #10 +
    '}';
  SaveStringToFile(Path, Content, False);
end;

// ------------------------------------------------------------
// [08.09] PULIZIA PRE-INSTALLAZIONE + SCRITTURA SETTINGS POST-INSTALL
// ------------------------------------------------------------
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssInstall then
  begin
    if DirExists(WizardDirValue) then
      CleanAppFolders(WizardDirValue);
  end;

  if CurStep = ssPostInstall then
    WritePersistentSettings(WizardDirValue, GetLangCode);
end;

// ------------------------------------------------------------
// [08.10] DISINSTALLAZIONE
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

    if DeleteWorkFiles then
    begin
      if DirExists(ExpandConstant('{app}\Audio_Input'))     then DelTree(ExpandConstant('{app}\Audio_Input'),     True, True, True);
      if DirExists(ExpandConstant('{app}\Audio_Extracted')) then DelTree(ExpandConstant('{app}\Audio_Extracted'), True, True, True);
      if DirExists(ExpandConstant('{app}\Dubbed'))          then DelTree(ExpandConstant('{app}\Dubbed'),          True, True, True);
      if DirExists(ExpandConstant('{app}\Output'))          then DelTree(ExpandConstant('{app}\Output'),          True, True, True);
      if DirExists(ExpandConstant('{app}\Transcripts'))     then DelTree(ExpandConstant('{app}\Transcripts'),     True, True, True);
      if DirExists(ExpandConstant('{app}\Translated'))      then DelTree(ExpandConstant('{app}\Translated'),      True, True, True);
      if DirExists(ExpandConstant('{app}\Video_Input'))     then DelTree(ExpandConstant('{app}\Video_Input'),     True, True, True);
      if DirExists(ExpandConstant('{app}\Logs'))            then DelTree(ExpandConstant('{app}\Logs'),            True, True, True);
    end;
  end;

  if CurUninstallStep = usPostUninstall then
    MsgBox(CustomMessage('UninstallRemainingMsg'), mbInformation, MB_OK);
end;