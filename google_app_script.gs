function doGet(e) {
  var folderName = "LIVE"; // Folder where you store your .deb files
  var folder, files, latestFile, latestDate = 0, latestId = "", latestName = "";

  // Get all folders in your Drive
  var folders = DriveApp.getFoldersByName(folderName);
  if (!folders.hasNext()) {
    return ContentService.createTextOutput(JSON.stringify({"error": "Folder not found"})).setMimeType(ContentService.MimeType.JSON);
  }
  folder = folders.next(); // Get the LIVE folder

  // Get all files in the LIVE folder
  files = folder.getFiles();
  while (files.hasNext()) {
    var file = files.next();
    var createdDate = file.getLastUpdated().getTime();
    if (createdDate > latestDate && file.getName().endsWith(".deb")) { // Only check .deb files
      latestDate = createdDate;
      latestFile = file;
      latestId = file.getId();
      latestName = file.getName();
    }
  }

  if (latestId === "" || latestName === "") {
    return ContentService.createTextOutput(JSON.stringify({"error": "No .deb files found"})).setMimeType(ContentService.MimeType.JSON);
  }

  var response = {
    "file_id": latestId,
    "file_name": latestName
  };

  return ContentService.createTextOutput(JSON.stringify(response)).setMimeType(ContentService.MimeType.JSON);
}
