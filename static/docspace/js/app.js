var fixedDom = document.getElementById("site-description");
var fixedInit = getElementViewTop(fixedDom);
window.onscroll = function(){
  var top = getElementViewTop(fixedDom);
  var scrollTop = document.documentElement.scrollTop || document.body.scrollTop;
  scrollTop > fixedInit ? fixedDom.classList.add('shadow-sm', 'fixed-top') : fixedDom.classList.remove('shadow-sm', 'fixed-top');
}

function getElementViewTop(element){
  var actualTop = element.offsetTop, elementScrollTop=document.body.scrollTop;
  return actualTop-elementScrollTop;
}

function ToTopscroll(){
  var currentScroll = document.documentElement.scrollTop || document.body.scrollTop;
  if (currentScroll > 0) {
       window.requestAnimationFrame(ToTopscroll);
       window.scrollTo (0,currentScroll - (currentScroll/5));
  }
}

var HasToTop = document.querySelector('#site-description-title');
if(HasToTop){
  HasToTop.style.cursor = 'pointer';
  HasToTop.addEventListener("click", ToTopscroll);
}

var ac = document.getElementById("site-content").querySelector('.article-content');
if(ac){
  var imgs = ac.querySelectorAll('img');
  var pres = ac.querySelectorAll('pre, blockquote');
  var codes = ac.querySelectorAll('code');
  [].forEach.call(imgs, function(img) {
    img.classList.add('img-fluid', 'mt-sm-2', 'mt-xs-1', 'rounded');
  });
  [].forEach.call(pres, function(pre){
    pre.classList.add('pl-3', 'p-2', 'bg-light', 'border-left');
  });
}
