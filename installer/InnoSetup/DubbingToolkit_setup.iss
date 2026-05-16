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
ExtraDiskSpaceRequired=16106127360
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
english.ReadyToInstall=The program is ready to install.%n%nNote: on first launch the app will download required dependencies (~8-10 GB).%nAn internet connection and at least 15 GB of free disk space are needed.
english.ReadyToUpdate=A previous version was detected. The program is ready to update.%n%nNote: Python dependencies will be re-downloaded.%nDownload required: ~8-10 GB.%nAn internet connection is required.
italian.ReadyToInstall=Il programma è pronto per l'installazione.%n%nNota: al primo avvio l'app scaricherà le dipendenze necessarie (~8-10 GB).%nServono connessione internet attiva e almeno 15 GB liberi su disco.
italian.ReadyToUpdate=È stata rilevata una versione precedente. Il programma è pronto per l'aggiornamento.%n%nNota: le dipendenze Python verranno riscaricate.%nDownload richiesto: ~8-10 GB.%nServono connessione internet attiva.
french.ReadyToInstall=Le programme est prêt à être installé.%n%nRemarque : au premier lancement, l'app téléchargera les dépendances requises (~8-10 Go).%nUne connexion internet et au moins 15 Go d'espace disque libre sont nécessaires.
french.ReadyToUpdate=Une version précédente a été détectée. Le programme est prêt à être mis à jour.%n%nRemarque : les dépendances Python seront retéléchargées.%nTéléchargement requis : ~8-10 Go.%nUne connexion internet est nécessaire.
german.ReadyToInstall=Das Programm ist zur Installation bereit.%n%nHinweis: Beim ersten Start lädt die App die erforderlichen Abhängigkeiten herunter (~8-10 GB).%nInternetverbindung und mindestens 15 GB freier Speicherplatz werden benötigt.
german.ReadyToUpdate=Eine frühere Version wurde gefunden. Das Programm ist bereit für die Aktualisierung.%n%nHinweis: Python-Abhängigkeiten werden neu heruntergeladen.%nDownload erforderlich: ~8-10 GB.%nEine Internetverbindung wird benötigt.
spanish.ReadyToInstall=El programa está listo para instalarse.%n%nNota: en el primer inicio, la app descargará las dependencias necesarias (~8-10 GB).%nSe necesita conexión a internet y al menos 15 GB de espacio libre en disco.
spanish.ReadyToUpdate=Se detectó una versión anterior. El programa está listo para actualizarse.%n%nNota: las dependencias de Python se volverán a descargar.%nDescarga requerida: ~8-10 GB.%nSe necesita conexión a internet.
portuguese.ReadyToInstall=O programa está pronto para ser instalado.%n%nNota: na primeira execução, o app baixará as dependências necessárias (~8-10 GB).%nSão necessários conexão com a internet e pelo menos 15 GB de espaço livre em disco.
portuguese.ReadyToUpdate=Uma versão anterior foi detectada. O programa está pronto para ser atualizado.%n%nNota: as dependências Python serão baixadas novamente.%nDownload necessário: ~8-10 GB.%nÉ necessária uma conexão com a internet.
russian.ReadyToInstall=Программа готова к установке.%n%nПримечание: при первом запуске приложение загрузит необходимые зависимости (~8-10 ГБ).%nНужны подключение к интернету и не менее 15 ГБ свободного места на диске.
russian.ReadyToUpdate=Обнаружена предыдущая версия. Программа готова к обновлению.%n%nПримечание: зависимости Python будут загружены повторно.%nОбъём загрузки: ~8-10 ГБ.%nНеобходимо подключение к интернету.

; --- [02.03] DIALOG DISINSTALLAZIONE CHECKBOX ---
english.UninstallDataTitle=Data removal options
english.UninstallDataMsg=Select what you want to permanently delete:
english.UninstallSelectAll=Select all
english.UninstallDeselectAll=Deselect all
english.UninstallCredentials=Credentials and API keys (credentials folder)
english.UninstallBilling=Billing data - monthly TTS usage (Billing folder)
english.UninstallLogs=Session logs (Logs folder)
italian.UninstallDataTitle=Opzioni di rimozione dati
italian.UninstallDataMsg=Seleziona cosa vuoi eliminare definitivamente:
italian.UninstallSelectAll=Seleziona tutto
italian.UninstallDeselectAll=Deseleziona tutto
italian.UninstallCredentials=Credenziali e chiavi API (cartella credentials)
italian.UninstallBilling=Dati di fatturazione - consumo TTS mensile (cartella Billing)
italian.UninstallLogs=Log di sessione (cartella Logs)
french.UninstallDataTitle=Options de suppression des données
french.UninstallDataMsg=Sélectionnez ce que vous souhaitez supprimer définitivement :
french.UninstallSelectAll=Tout sélectionner
french.UninstallDeselectAll=Tout désélectionner
french.UninstallCredentials=Identifiants et clés API (dossier credentials)
french.UninstallBilling=Données de facturation - utilisation TTS mensuelle (dossier Billing)
french.UninstallLogs=Journaux de session (dossier Logs)
german.UninstallDataTitle=Optionen zur Datenlöschung
german.UninstallDataMsg=Wählen Sie aus, was Sie dauerhaft löschen möchten:
german.UninstallSelectAll=Alles auswählen
german.UninstallDeselectAll=Alles abwählen
german.UninstallCredentials=Anmeldedaten und API-Schlüssel (Ordner credentials)
german.UninstallBilling=Abrechnungsdaten - monatliche TTS-Nutzung (Ordner Billing)
german.UninstallLogs=Sitzungsprotokolle (Ordner Logs)
spanish.UninstallDataTitle=Opciones de eliminación de datos
spanish.UninstallDataMsg=Seleccione qué desea eliminar de forma permanente:
spanish.UninstallSelectAll=Seleccionar todo
spanish.UninstallDeselectAll=Deseleccionar todo
spanish.UninstallCredentials=Credenciales y claves API (carpeta credentials)
spanish.UninstallBilling=Datos de facturación - uso TTS mensual (carpeta Billing)
spanish.UninstallLogs=Registros de sesión (carpeta Logs)
portuguese.UninstallDataTitle=Opções de remoção de dados
portuguese.UninstallDataMsg=Selecione o que deseja excluir permanentemente:
portuguese.UninstallSelectAll=Selecionar tudo
portuguese.UninstallDeselectAll=Desmarcar tudo
portuguese.UninstallCredentials=Credenciais e chaves de API (pasta credentials)
portuguese.UninstallBilling=Dados de faturamento - uso TTS mensal (pasta Billing)
portuguese.UninstallLogs=Registros de sessão (pasta Logs)
russian.UninstallDataTitle=Параметры удаления данных
russian.UninstallDataMsg=Выберите, что вы хотите удалить навсегда:
russian.UninstallSelectAll=Выбрать всё
russian.UninstallDeselectAll=Снять всё
russian.UninstallCredentials=Учётные данные и ключи API (папка credentials)
russian.UninstallBilling=Данные о выставлении счетов - использование TTS (папка Billing)
russian.UninstallLogs=Журналы сеансов (папка Logs)

; --- [02.05] AVVISO, LAVORO E CONFERMA DISINSTALLAZIONE ---
english.UninstallWarning=WARNING: selected items will be permanently deleted.
english.UninstallWorkFiles=Work files - projects and user data (Workspace folder)
english.UninstallConfirmTitle=WARNING — Permanent deletion
english.UninstallConfirmText=This action cannot be undone.%nThe selected data will be permanently deleted and cannot be recovered.%n%nAre you sure you want to proceed?
english.UninstallConfirmYes=Yes, delete
english.UninstallConfirmCancel=Cancel
italian.UninstallWarning=ATTENZIONE: i dati selezionati verranno eliminati definitivamente.
italian.UninstallWorkFiles=File di lavoro - progetti e dati utente (cartella Workspace)
italian.UninstallConfirmTitle=ATTENZIONE — Eliminazione definitiva
italian.UninstallConfirmText=Questa operazione è irreversibile.%nI dati selezionati verranno eliminati definitivamente e non potranno essere recuperati.%n%nSei sicuro di voler procedere?
italian.UninstallConfirmYes=Sì, elimina
italian.UninstallConfirmCancel=Annulla
french.UninstallWarning=ATTENTION : les éléments sélectionnés seront supprimés définitivement.
french.UninstallWorkFiles=Fichiers de travail - projets et données utilisateur (dossier Workspace)
french.UninstallConfirmTitle=ATTENTION — Suppression définitive
french.UninstallConfirmText=Cette action est irréversible.%nLes données sélectionnées seront supprimées définitivement et ne pourront pas être récupérées.%n%nÊtes-vous sûr de vouloir continuer ?
french.UninstallConfirmYes=Oui, supprimer
french.UninstallConfirmCancel=Annuler
german.UninstallWarning=WARNUNG: Die ausgewählten Elemente werden dauerhaft gelöscht.
german.UninstallWorkFiles=Arbeitsdateien - Projekte und Benutzerdaten (Ordner Workspace)
german.UninstallConfirmTitle=WARNUNG — Endgültige Löschung
german.UninstallConfirmText=Diese Aktion kann nicht rückgängig gemacht werden.%nDie ausgewählten Daten werden endgültig gelöscht und können nicht wiederhergestellt werden.%n%nSind Sie sicher, dass Sie fortfahren möchten?
german.UninstallConfirmYes=Ja, löschen
german.UninstallConfirmCancel=Abbrechen
spanish.UninstallWarning=ADVERTENCIA: los elementos seleccionados se eliminarán permanentemente.
spanish.UninstallWorkFiles=Archivos de trabajo - proyectos y datos de usuario (carpeta Workspace)
spanish.UninstallConfirmTitle=ADVERTENCIA — Eliminación permanente
spanish.UninstallConfirmText=Esta acción es irreversible.%nLos datos seleccionados se eliminarán permanentemente y no podrán recuperarse.%n%n¿Está seguro de que desea continuar?
spanish.UninstallConfirmYes=Sí, eliminar
spanish.UninstallConfirmCancel=Cancelar
portuguese.UninstallWarning=AVISO: os itens selecionados serão excluídos permanentemente.
portuguese.UninstallWorkFiles=Arquivos de trabalho - projetos e dados do usuário (pasta Workspace)
portuguese.UninstallConfirmTitle=AVISO — Exclusão permanente
portuguese.UninstallConfirmText=Esta ação é irreversível.%nOs dados selecionados serão excluídos permanentemente e não poderão ser recuperados.%n%nTem certeza de que deseja continuar?
portuguese.UninstallConfirmYes=Sim, excluir
portuguese.UninstallConfirmCancel=Cancelar
russian.UninstallWarning=ВНИМАНИЕ: выбранные элементы будут удалены безвозвратно.
russian.UninstallWorkFiles=Рабочие файлы - проекты и данные пользователя (папка Workspace)
russian.UninstallConfirmTitle=ВНИМАНИЕ — Безвозвратное удаление
russian.UninstallConfirmText=Это действие необратимо.%nВыбранные данные будут удалены безвозвратно и не смогут быть восстановлены.%n%nВы уверены, что хотите продолжить?
russian.UninstallConfirmYes=Да, удалить
russian.UninstallConfirmCancel=Отмена

; --- [02.06] AVVIO POST-INSTALLAZIONE ---
english.LaunchDescription=Launch Dubbing Toolkit
italian.LaunchDescription=Avvia Dubbing Toolkit
french.LaunchDescription=Lancer Dubbing Toolkit
german.LaunchDescription=Dubbing Toolkit starten
spanish.LaunchDescription=Iniciar Dubbing Toolkit
portuguese.LaunchDescription=Iniciar o Dubbing Toolkit
russian.LaunchDescription=Запустить Dubbing Toolkit

; --- [02.04] MESSAGGIO FINALE DISINSTALLAZIONE ---
english.UninstallRemainingMsg=If work files or credentials were preserved, the following folders may still be present in the installation folder:%n%n  - Workspace  (projects, audio, video, transcripts, etc.)%n  - Billing%n  - credentials%n  - Logs%n%nYou can find them in the installation folder and delete them manually if you no longer need them.
italian.UninstallRemainingMsg=Se i file di lavoro o le credenziali sono stati preservati, le seguenti cartelle potrebbero essere ancora presenti nella cartella di installazione:%n%n  - Workspace  (progetti, audio, video, trascrizioni, ecc.)%n  - Billing%n  - credentials%n  - Logs%n%nLe trovi nella cartella di installazione. Puoi eliminarle manualmente se non ti servono più.
french.UninstallRemainingMsg=Si les fichiers de travail ou les identifiants ont été conservés, les dossiers suivants peuvent encore être présents dans le dossier d'installation :%n%n  - Workspace  (projets, audio, vidéo, transcriptions, etc.)%n  - Billing%n  - credentials%n  - Logs%n%nVous les trouverez dans le dossier d'installation. Vous pouvez les supprimer manuellement si vous n'en avez plus besoin.
german.UninstallRemainingMsg=Wenn Arbeitsdateien oder Anmeldedaten beibehalten wurden, können die folgenden Ordner noch im Installationsordner vorhanden sein:%n%n  - Workspace  (Projekte, Audio, Video, Transkripte usw.)%n  - Billing%n  - credentials%n  - Logs%n%nSie finden sie im Installationsordner. Sie können sie manuell löschen, wenn Sie sie nicht mehr benötigen.
spanish.UninstallRemainingMsg=Si los archivos de trabajo o las credenciales se han conservado, las siguientes carpetas pueden seguir presentes en la carpeta de instalación:%n%n  - Workspace  (proyectos, audio, vídeo, transcripciones, etc.)%n  - Billing%n  - credentials%n  - Logs%n%nPuede encontrarlas en la carpeta de instalación. Puede eliminarlas manualmente si ya no las necesita.
portuguese.UninstallRemainingMsg=Se os arquivos de trabalho ou credenciais foram preservados, as seguintes pastas ainda podem estar presentes na pasta de instalação:%n%n  - Workspace  (projetos, áudio, vídeo, transcrições, etc.)%n  - Billing%n  - credentials%n  - Logs%n%nVocê pode encontrá-las na pasta de instalação. Pode excluí-las manualmente se não precisar mais delas.
russian.UninstallRemainingMsg=Если рабочие файлы или учётные данные были сохранены, следующие папки могут ещё находиться в папке установки:%n%n  - Workspace  (проекты, аудио, видео, транскрипции и др.)%n  - Billing%n  - credentials%n  - Logs%n%nВы найдёте их в папке установки. Вы можете удалить их вручную, если они вам больше не нужны.

; ============================================================
; [03] PAYLOAD (generato automaticamente da build_manifest.ps1)
; ============================================================
#include "payload_sections.iss"

; ============================================================
; [05] SHORTCUT
; ============================================================
[Icons]
; --- Desktop ---
Name: "{commondesktop}\Dubbing Toolkit";             Filename: "{app}\StartDubbing.bat";       IconFilename: "{app}\assets\DubbingToolkit_Studio.ico"
Name: "{commondesktop}\Dubbing Toolkit - Projects";  Filename: "{app}\Workspace\projects";     IconFilename: "{app}\assets\DubbingToolkit_Workspace.ico"

; --- Start Menu ---
Name: "{group}\Dubbing Toolkit";                     Filename: "{app}\StartDubbing.bat";       IconFilename: "{app}\assets\DubbingToolkit_Studio.ico"
Name: "{group}\Projects";                            Filename: "{app}\Workspace\projects";     IconFilename: "{app}\assets\DubbingToolkit_Workspace.ico"
Name: "{group}\Documentation";                       Filename: "{app}\Docs";                   IconFilename: "{app}\assets\DubbingToolkit_Studio.ico"


; ============================================================
; [06] PULIZIA PRE-INSTALLAZIONE (venv — gestita dal motore InnoSetup)
; ============================================================
; venv is deleted here (not in Pascal Code) so InnoSetup's own engine
; handles the deletion with message pump active — no frozen window.
[InstallDelete]
Type: filesandordirs; Name: "{app}\venv"

; ============================================================
; [07] AVVIO POST-INSTALLAZIONE
; ============================================================
[Run]
Filename: "{app}\StartDubbing.bat"; Description: "{cm:LaunchDescription}"; Flags: nowait postinstall

; ============================================================
; [08] CODICE PASCAL
; ============================================================
[Code]

// ------------------------------------------------------------
// [08.01] VARIABILI GLOBALI
// ------------------------------------------------------------
var
  DeleteCredentials:    Boolean;
  DeleteBilling:        Boolean;
  DeleteLogs:           Boolean;
  DeleteWorkFiles:      Boolean;
  IsUpgrade:            Boolean;
  GChkCred:             TCheckBox;
  GChkBilling:          TCheckBox;
  GChkLogs:             TCheckBox;
  GChkWork:             TCheckBox;
  GConfirmDeleteResult: Boolean;

// ------------------------------------------------------------
// [08.02a] FORM CONFERMA ELIMINAZIONE
// ------------------------------------------------------------
procedure ConfirmDeleteYesClick(Sender: TObject);
begin
  GConfirmDeleteResult := True;
end;

function ShowConfirmDeleteForm: Boolean;
var
  Form:      TForm;
  LblTitle:  TLabel;
  LblBody:   TLabel;
  BtnYes:    TButton;
  BtnCancel: TButton;
begin
  Result := False;

  Form := TForm.Create(nil);
  Form.Caption      := CustomMessage('UninstallConfirmTitle');
  Form.ClientWidth  := 480;
  Form.ClientHeight := 210;
  Form.Position     := poScreenCenter;
  Form.BorderStyle  := bsDialog;

  LblTitle := TLabel.Create(Form);
  LblTitle.Parent     := Form;
  LblTitle.AutoSize   := False;
  LblTitle.Left       := 20;
  LblTitle.Top        := 18;
  LblTitle.Width      := 440;
  LblTitle.Height     := 22;
  LblTitle.Caption    := CustomMessage('UninstallConfirmTitle');
  LblTitle.Font.Style := [fsBold];
  LblTitle.Font.Color := clRed;
  LblTitle.Font.Size  := 10;

  LblBody := TLabel.Create(Form);
  LblBody.Parent    := Form;
  LblBody.AutoSize  := False;
  LblBody.Left      := 20;
  LblBody.Top       := 52;
  LblBody.Width     := 440;
  LblBody.Height    := 90;
  LblBody.WordWrap  := True;
  LblBody.Caption   := CustomMessage('UninstallConfirmText');

  BtnCancel := TButton.Create(Form);
  BtnCancel.Parent      := Form;
  BtnCancel.Caption     := CustomMessage('UninstallConfirmCancel');
  BtnCancel.Left        := 250;
  BtnCancel.Top         := 168;
  BtnCancel.Width       := 100;
  BtnCancel.ModalResult := mrCancel;

  BtnYes := TButton.Create(Form);
  BtnYes.Parent      := Form;
  BtnYes.Caption     := CustomMessage('UninstallConfirmYes');
  BtnYes.Left        := 360;
  BtnYes.Top         := 168;
  BtnYes.Width       := 100;
  BtnYes.ModalResult := mrOK;
  BtnYes.OnClick     := @ConfirmDeleteYesClick;

  GConfirmDeleteResult := False;
  Form.ShowModal;
  Result := GConfirmDeleteResult;
  Form.Free;
end;

// ------------------------------------------------------------
// [08.02b] HANDLER PULSANTI SELEZIONA/DESELEZIONA TUTTO
// ------------------------------------------------------------
procedure SelectAllClick(Sender: TObject);
begin
  GChkCred.Checked    := True;
  GChkBilling.Checked := True;
  GChkLogs.Checked    := True;
  GChkWork.Checked    := True;
end;

procedure DeselectAllClick(Sender: TObject);
begin
  GChkCred.Checked    := False;
  GChkBilling.Checked := False;
  GChkLogs.Checked    := False;
  GChkWork.Checked    := False;
end;

// ------------------------------------------------------------
// [08.02] FORM CHECKBOX DISINSTALLAZIONE
// ------------------------------------------------------------
procedure ShowUninstallOptionsForm;
var
  Form:          TForm;
  LblWarning:    TLabel;
  LblMsg:        TLabel;
  BtnSelectAll:  TButton;
  BtnDeselectAll: TButton;
  BtnOK:         TButton;
  Confirmed:     Boolean;
begin
  DeleteCredentials := False;
  DeleteBilling     := False;
  DeleteLogs        := False;
  DeleteWorkFiles   := False;

  repeat
    Confirmed := True;

    Form := TForm.Create(nil);
    Form.Caption      := CustomMessage('UninstallDataTitle');
    Form.ClientWidth  := 480;
    Form.ClientHeight := 370;
    Form.Position     := poScreenCenter;
    Form.BorderStyle  := bsDialog;

    LblWarning := TLabel.Create(Form);
    LblWarning.Parent     := Form;
    LblWarning.AutoSize   := False;
    LblWarning.Left       := 20;
    LblWarning.Top        := 15;
    LblWarning.Width      := 440;
    LblWarning.Height     := 36;
    LblWarning.WordWrap   := True;
    LblWarning.Caption    := CustomMessage('UninstallWarning');
    LblWarning.Font.Style := [fsBold];
    LblWarning.Font.Color := clRed;

    LblMsg := TLabel.Create(Form);
    LblMsg.Parent  := Form;
    LblMsg.Left    := 20;
    LblMsg.Top     := 62;
    LblMsg.Width   := 440;
    LblMsg.Caption := CustomMessage('UninstallDataMsg');

    BtnSelectAll := TButton.Create(Form);
    BtnSelectAll.Parent   := Form;
    BtnSelectAll.Caption  := CustomMessage('UninstallSelectAll');
    BtnSelectAll.Left     := 20;
    BtnSelectAll.Top      := 85;
    BtnSelectAll.Width    := 140;
    BtnSelectAll.Height   := 24;
    BtnSelectAll.OnClick  := @SelectAllClick;

    BtnDeselectAll := TButton.Create(Form);
    BtnDeselectAll.Parent   := Form;
    BtnDeselectAll.Caption  := CustomMessage('UninstallDeselectAll');
    BtnDeselectAll.Left     := 170;
    BtnDeselectAll.Top      := 85;
    BtnDeselectAll.Width    := 140;
    BtnDeselectAll.Height   := 24;
    BtnDeselectAll.OnClick  := @DeselectAllClick;

    GChkCred := TCheckBox.Create(Form);
    GChkCred.Parent  := Form;
    GChkCred.Left    := 20;
    GChkCred.Top     := 122;
    GChkCred.Width   := 440;
    GChkCred.Caption := CustomMessage('UninstallCredentials');
    GChkCred.Checked := DeleteCredentials;

    GChkBilling := TCheckBox.Create(Form);
    GChkBilling.Parent  := Form;
    GChkBilling.Left    := 20;
    GChkBilling.Top     := 150;
    GChkBilling.Width   := 440;
    GChkBilling.Caption := CustomMessage('UninstallBilling');
    GChkBilling.Checked := DeleteBilling;

    GChkLogs := TCheckBox.Create(Form);
    GChkLogs.Parent  := Form;
    GChkLogs.Left    := 20;
    GChkLogs.Top     := 178;
    GChkLogs.Width   := 440;
    GChkLogs.Caption := CustomMessage('UninstallLogs');
    GChkLogs.Checked := DeleteLogs;

    GChkWork := TCheckBox.Create(Form);
    GChkWork.Parent  := Form;
    GChkWork.Left    := 20;
    GChkWork.Top     := 206;
    GChkWork.Width   := 440;
    GChkWork.Caption := CustomMessage('UninstallWorkFiles');
    GChkWork.Checked := DeleteWorkFiles;

    BtnOK := TButton.Create(Form);
    BtnOK.Parent      := Form;
    BtnOK.Caption     := 'OK';
    BtnOK.Left        := 195;
    BtnOK.Top         := 320;
    BtnOK.Width       := 90;
    BtnOK.ModalResult := mrOK;

    Form.ShowModal;

    DeleteCredentials := GChkCred.Checked;
    DeleteBilling     := GChkBilling.Checked;
    DeleteLogs        := GChkLogs.Checked;
    DeleteWorkFiles   := GChkWork.Checked;

    Form.Free;

    if DeleteCredentials or DeleteBilling or DeleteLogs or DeleteWorkFiles then
    begin
      if not ShowConfirmDeleteForm then
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
  AppFolders.Add('Config');
  AppFolders.Add('Settings');
  AppFolders.Add('Docs');
  AppFolders.Add('voices');
// ##CLEANUP_END##
  // Note: venv is handled by [InstallDelete] to keep the installer responsive
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
    '  "first_run": true,' + #10 +
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

    if DeleteLogs then
      if DirExists(ExpandConstant('{app}\Logs')) then
        DelTree(ExpandConstant('{app}\Logs'), True, True, True);

    if DeleteWorkFiles then
      if DirExists(ExpandConstant('{app}\Workspace')) then
        DelTree(ExpandConstant('{app}\Workspace'), True, True, True);

    if DirExists(ExpandConstant('{app}\venv')) then
      DelTree(ExpandConstant('{app}\venv'), True, True, True);
  end;

  if CurUninstallStep = usPostUninstall then
    MsgBox(CustomMessage('UninstallRemainingMsg'), mbInformation, MB_OK);
end;