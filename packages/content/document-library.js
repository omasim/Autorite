(() => {
 const form=document.querySelector('.library-toolbar');
 if(!form)return;
 const search=document.getElementById('document-search');
 const category=document.getElementById('document-category');
 const cards=[...document.querySelectorAll('.document-card')];
 const groups=[...document.querySelectorAll('.document-group')];
 const update=()=>{
  const words=search.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
  let count=0;
  for(const card of cards){
   const matches=(!category.value||card.dataset.category===category.value)&&words.every(word=>card.dataset.search.includes(word));
   card.hidden=!matches;if(matches)count++;
  }
  for(const group of groups)group.hidden=![...group.querySelectorAll('.document-card')].some(card=>!card.hidden);
  document.querySelector('.document-count').textContent=`${count} of ${cards.length} documents`;
  document.querySelector('.document-empty').hidden=count!==0;
 };
 search.addEventListener('input',update);category.addEventListener('change',update);
 form.addEventListener('reset',()=>{search.value='';category.value='';update();search.focus();});
})();
