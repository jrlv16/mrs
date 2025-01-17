/* globals $ */
import 'expose-loader?jQuery!jquery'
import 'expose-loader?$!jquery'
import Cookie from 'js-cookie'
import 'blueimp-file-upload'

var formInit = function(form) {
  var $form = $(form)

  $(form).on('click', '[data-delete-url]', function() {
    var $a = $(this)
    $.ajax({
      method: 'DELETE',
      url: $(this).attr('data-delete-url'),
      error: function() {
        // console.log('error')
      },
      success: function() {
        $a.parents('li').slideUp()
      },
      beforeSend: function(xhr) {
        if (!this.crossDomain) {
          xhr.setRequestHeader('X-CSRFToken', Cookie.get('csrftoken'))
        }
      }
    })
  })

  var formData = $form.serializeArray()
  formData.push({
    name: 'csrfmiddlewaretoken',
    value: Cookie.get('csrftoken')
  })

  var constants = {
    validExtensions: [
      'jpeg',
      'jpg',
      'png',
      'pdf'
    ],
    maxFileSize: 4096 * 1024,
    errorMsg: {
      mimeType: 'Extension de fichier refusé',
      fileSize: 'Fichier trop lourd (4MB max.)'
    }
  }

  //// validate file MIME type
  //// private, tested through this.validateFile
  // mimeType (string): file mime type
  function extensionValidate(ext) {
    // todo: print mimetypes to user if not valid
    // Due to some versions IE11 failing to send a non-empty mimetype, use ext
    return constants.validExtensions.indexOf(ext) >= 0
  }

  //// Validate file size
  //// private, tested through this.validateFile
  // size (int): file size (bytes)
  function fileSizeValidate(size) {
    // todo: print maxsize to user if not valid
    return size <= constants.maxFileSize
  }

  //// Upload file validation
  // file (file object): upload file object
  function validateFile(file) {
    // todo: raise both errors is better for the user
    var parts = file.name.split('.')
    var ext = parts[parts.length - 1].toLowerCase()

    if (!extensionValidate(ext)) {
      throw `${constants.errorMsg.mimeType}: ${ext}`
    }

    if (!fileSizeValidate(file.size)) {
      throw `${constants.errorMsg.fileSize}: ${file.size} / ${constants.maxFileSize}`
    }
  }

  function createErrorMsg(e) {
    return `<span class="error">${e}</span>`
  }

  $('[data-upload-url][type=file]').each(function() {
    var $file = $(this)
    var $target = $file.parents('.input-field').find('ul.files')
    if (!$target.length) {
      // admin form
      $target = $file.parent().find('ul.files')
    }
    var url = $(this).attr('data-upload-url').replace(
      'MRSREQUEST_UUID', $('[name=mrsrequest_uuid]').val())
    $file.fileupload({
      url: url,
      formData: formData,
      // maxFileSize: Math.pow(10, 7),
      // acceptFileTypes: /(\.|\/)(gif|jpe?g|png|pdf)$/i,
      add: function (e, data) {
        data.context = []

        for (var i in data.files) {
          var file = data.files[i]
          var template

          try {
            if (!$file.is('[multiple=multiple]')) {
              $target.find('li').remove()
            }

            validateFile(file)

            template = `
              <li data-file-name="${file.name}">
                <a class="file-name">${file.name}</a>
                <progress max="${file.size}" value="0" class="progress-bar">
                </progress>
              </li>
            `
          } catch(e) {
            template = `
               <li data-file-name="${file.name}">
                    ${createErrorMsg(e)}
               </li>
            `
          }

          data.context.push($(template).appendTo($target))
        }

        data.submit()
      },
      progressall: function () {
        // console.log('progressall', e, data)
      },
      progress: function (e, data) {
        for (var i in data.files) {
          var $li = data.context[i]
          $li.find('progress').val(data.loaded)
        }
      },
      done: function (e, data) {
        var result = JSON.parse(data.result)['files']
        for (var i in result) {
          var file = result[i]
          var $li = data.context[i]
          $(`
            <a data-delete-url="${file.deleteUrl}" class="delete-file">
              Effacer
            </a>
          `).appendTo($li)
          $li.find('a.file-name').attr('target', '_blank')
          $li.find('a.file-name').attr('href', file.thumbnailUrl)
          $li.find('progress').fadeOut()
        }
      },
      fail: function (e, data) {
        for (var i in data.files) {
          var $li = data.context[i]
          var response = data.response()
          $(createErrorMsg(response.errorThrown)).appendTo($li)
          $li.find('progress').fadeOut()
        }
      }
    })
  })
}

export default formInit
