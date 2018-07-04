var comments = document.getElementById("comments-list");
var remove_class = (ele, cls) => ele.classList.remove(cls);
var add_class = (ele, cls) => ele.classList.add(cls);

var reply_reset = function(){
  document.getElementById('id_parent').value=null;
  var last = document.querySelectorAll('div.p-2.mb-3.mt-2.border-bottom.border-light.bg-light');
  [].forEach.call(last, function(l) {
    remove_class(l, 'bg-light');
    //l.classList.remove('bg-light');
  });
  var two = comments.querySelectorAll('a.float-right.badge.badge-light.text-muted');
  two.forEach(function(t){
    add_class(t, 'd-none');
    //t.classList.add('d-none');
  });
}
var gravatar = document.getElementById("comment-gravatar");
gravatar.addEventListener("click", function(){
  var CommentAuthorInfo = document.getElementById("comment-author-info");
  //if CommentAuthorInfo.getAttribute("data-show")
})

if(comments){
  var form = document.getElementById("comment-form");
  var cols = comments.querySelectorAll('a.badge');
  [].forEach.call(cols, function(col) {
    col.addEventListener("click", function(){
      action = this.getAttribute("data-action");
      if (action == 'reply'){
        reply_reset();
        var parent = this.parentNode;
        parent.lastElementChild.classList.remove('d-none');
        parent.classList.add('bg-light');
        parent.appendChild(form);
        document.getElementById('id_parent').value=this.getAttribute("data-id");
        document.getElementById('id_content').focus();
      } else if (action == 'cancel'){
        reply_reset();
        document.getElementsByClassName('comments-list')[0].appendChild(form);
      } else if (action == 'like'){
        var liked =  this.getAttribute('data-push');
        if (liked !== true){
          var like_count = this.children[0].innerText;
          this.children[0].innerText = parseInt(this.children[0].innerText)+1;
        }
      }
    });
  });
}