// Ref:

// https://developers.google.com/drive/v3/web/quickstart/nodejs
// https://github.com/google/google-api-nodejs-client#using-jwt-service-tokens

const google = require('googleapis');
const fs = require('fs');

let config = {};
try {
  config = require('./gdrive.json');
} catch(err) {
  console.log("no gdrive.json");
  config.client_email = process.env.drive_email;
  config.private_key  = process.env.drive_key;
}

console.log("config:", config);
if (!config.client_email || !config.private_key) {
  console.log("no config data, exit");
  return;
}

let jwtClient = new google.auth.JWT(
  config.client_email,
  null,
  config.private_key,
  ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive.metadata"],
  null
  // "acdc_soft@asiaa.sinica.edu.tw" //null
);

// https://github.com/extrabacon/google-oauth-jwt
// service account -> download json file
// json file-> be used automatically to get JWT token in google api
// token can be used for curl, https://getblimp.github.io/django-rest-framework-jwt/
// curl -H "Authorization: JWT <your_token>"
// oauth is a flow/protocal, not the token it self, so can work with JWT token
// Now that the Service Account has permission to some user resources, the application can query the API with OAuth2. When using OAuth2

// https://github.com/google/google-api-nodejs-client/issues/431
// authData.email,
// authData.keyFile,
// authData.key,
// authData.scopes,
// authData.subject
//http://isd-soft.com/tech_blog/accessing-google-apis-using-service-account-node-js/

// https://www.googleapis.com/auth/drive.file	View and manage Google Drive files and folders that you have opened or created with this app

let drive = google.drive({ version: 'v3', auth: jwtClient });

//1st part
jwtClient.authorize(function (err, tokens) {
  if (err) {
    console.log(err);
    return;
  }

  // getFilelist();

  drive.files.list({
    auth: jwtClient,
  }, function (err, resp) {

    console.log("err:", err);
    console.log("resp:", resp);

    const files = resp.files;
    for (let file of files) {
      if (file.name = 'autobuild') {
        console.log("bingo:", file.id);
        // console.log("date:", new Date());
        // TRAVIS_BUILD_NUMBER

        const originFile = "Carta-10.12-0.9.0.dmg";

        let dateObj = new Date();
        let month = dateObj.getUTCMonth() + 1; //months from 1-12
        let day = dateObj.getUTCDate();
        let year = dateObj.getUTCFullYear();

        let newdate = year + "-" + month + "-" + day;
        console.log("day:", newdate);
        let targetFile = "CARTA-"+newdate;
        if (process.env.TRAVIS_BUILD_NUMBER) {
          targetFile = targetFile+"-"+process.env.TRAVIS_BUILD_NUMBER;
        }
        targetFile =targetFile+".dmg";
        // const trageFile = originFile;
        console.log("BUILD NUMBER:", targetFile);

        writeFile(binaryFileContent(trageFile, 'application/x-apple-diskimage',
        originFile, ["0B6SSpI8M8o7uRUtwV1Z3MGwtVGM"]));
      }
    }
    // handle err and response
  });

  // { kind: 'drive#file',
  //      id: '0B6SSpI8M8o7uRUtwV1Z3MGwtVGM',
  //      name: 'autobuild',
  //      mimeType: 'application/vnd.google-apps.folder' },

 // writeFile(textFileContent("c.txt", "apple", ["0B6SSpI8M8o7uRUtwV1Z3MGwtVGM"]));
  // writeFile(imageFileContent("d.png", "selection.png", ["0B6SSpI8M8o7uRUtwV1Z3MGwtVGM"]));
//  writeFile(imageFileContent("d.png", 'image/png', "selection.png", ["0B6SSpI8M8o7uRUtwV1Z3MGwtVGM"]));

});

// https://github.com/google/google-api-nodejs-client#exposing-request-object
// Exposing request object
//
// Every request to the API returns a request object, allowing you to track the request's progress or general information about the request.
//
// var req = drive.files.create(/* ... */);
// console.log(req.uri.href);

function getFilelist() {

  // Make an authorized request to list Drive files.
  drive.files.list({
    auth: jwtClient,
  }, function (err, resp) {

    console.log("err:", err);
    console.log("resp:", resp);
    // handle err and response
  });

}

const helloWordText = {
  resource: {
    name: 'Test',
    mimeType: 'text/plain'
  },
  media: {
    mimeType: 'text/plain',
    body: 'Hello World'
  }
};

// https://developers.google.com/drive/v2/reference/files/insert, so mime/content type should be arbitrary
function textFileContent(fileName, text, folders) {

  let content =  {
    //fileMetadata
    resource: {
      name: fileName,
      // mimeType: 'text/plain'
    },
    //media
    media: {
      mimeType: 'text/plain',
      body: text
    },
    fields: 'id' // return file/resp has id field, e.g. resp.id
  };

  if (folders) {
    content.resource.parents = folders;
  }

  return content;

}

function binaryFileContent(fileName, contentType, path, folders) {

  let content =  {
    //fileMetadata
    resource: {
      name: fileName,
      // mimeType: 'text/plain'
    },
    //media
    media: {
      mimeType: contentType, //'image/png',
      body: fs.createReadStream(path)
    },
    fields: 'id' // return file/resp has id field, e.g. resp.id
  };

  if (folders) {
    content.resource.parents = folders;
  }

  return content;

}

//'application/x-apple-diskimage'
//https://stackoverflow.com/questions/25916179/when-serving-dmg-files-from-php-user-is-getting-disk-image-not-recognized

//https://stackoverflow.com/questions/11894772/google-drive-mime-types-listing
//"txt"=>'text/plain',
//"zip"=>'application/zip',
//"pdf"=> 'application/pdf',
//"js"=>'text/js',
// "rar"=>'application/rar',
// "tar"=>'application/tar',
// "html"=>'text/html',
// "default"=>'application/octet-stream', ???
// "folder"=>'application/vnd.google-apps.folder'

// google doc mime type: https://developers.google.com/drive/v3/web/mime-types?hl=zh-TW

function writeHelloWorldFile() {
  drive.files.create(helloWordText
    , function (err, resp) {

    console.log("err2:", err);
    console.log("resp2:", resp);
    // handle err and response
  });
}

function writeFile(content) {
  // let folderId = '0BwwA4oUTeiV1TGRPeTVjaWRDY1E';

  // let fileMetadata = {
  //   'name': 'photo.jpg',
  //   parents: [ folderId ]
  // };
  // let media = {
  //   mimeType: 'image/jpeg',
  //   body: fs.createReadStream('files/photo.jpg')
  // };

  drive.files.create(content , function(err, file) {
    if (err) {
      // Handle error
      console.log(err);
    } else {
      console.log('File Id: ', file.id);
    }
  });
}

function createFolder() {
  let fileMetadata = {
    'name' : 'Invoices',
    'mimeType' : 'application/vnd.google-apps.folder'
  };

  drive.files.create({
    resource: fileMetadata,
    fields: 'id'
  }, function(err, file) {
    if (err) {
      // Handle error
      console.log(err);
    } else {
      console.log('Folder Id: ', file.id);
    }
  });
}

//2nd part
// let req = drive.files.create(/* ... */);
// console.log(req.uri.href); // print out the request's URL.

//3rd
// You can also override request options per request, such as url, method, and encoding.
//
// For example:
//
// drive.files.export({
//   fileId: 'asxKJod9s79', // A Google Doc
//   mimeType: 'application/pdf'
// }, {
//   encoding: null // Make sure we get the binary data
// }, function (err, buffer) {
//   // ...
// });
