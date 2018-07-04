(function() {
  $(function() {
    var $preview, editor, mobileToolbar, toolbar;
    Simditor.locale = 'zh-CN';
    toolbar = ['title', 'bold', 'italic', 'underline', 'strikethrough', 'fontScale', 'color', '|', 'ol', 'ul', 'blockquote', 'code', 'table', '|', 'link', 'image', 'hr', '|', 'indent', 'outdent', 'alignment', 'fullscreen', 'html'];
    mobileToolbar = ["bold", "underline", "strikethrough", "color", "ul", "ol"];
    if (mobilecheck()) {
      toolbar = mobileToolbar;
    }
    editor = new Simditor({
      textarea: $('#id_content'),
      placeholder: '这里输入文字...',
      toolbar: toolbar,
      pasteImage: true,
      autosave: 'editor-content',
      defaultImage: 'images/image.png',
      upload : {
		    url : '/simditor/upload/',
		    //params: null,
		    fileKey: 'upload',
		    connectionCount: 3,
		    leaveConfirm: '正在上传文件'
      }
    });
    $preview = $('#preview');
    if ($preview.length > 0) {
      return editor.on('valuechanged', function(e) {
        return $preview.html(editor.getValue());
      });
    }
  });

}).call(this);
