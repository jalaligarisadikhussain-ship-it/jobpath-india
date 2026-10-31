import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {isVideoConfigReady,mountProfessionalVideo} from '../assets/js/video-ads.mjs';

const live = JSON.parse(readFileSync('data/video-ads-config.json','utf8'));
const approved = {
  enabled:true,status:'approved',provider:'vdo.ai',mode:'provider-iframe',
  publisherApproved:true,categoryExclusionsConfirmed:true,
  mutedPlaybackVerified:true,closeControlVerified:true,
  requiresExplicitOptIn:true,embedUrl:'https://approved-video.example/embed/123',
  embedHost:'approved-video.example'
};
test('production defaults fail closed; no fake ad tag',()=>{
  assert.equal(live.enabled,false);
  assert.equal(live.embedUrl,'');
  assert.equal(isVideoConfigReady(live,'jobpath-india.pages.dev'),false);
});
test('approval, clean-category and UX gates are mandatory',()=>{
  assert.equal(isVideoConfigReady(approved,'jobpath-india.pages.dev'),true);
  for(const key of ['enabled','publisherApproved','categoryExclusionsConfirmed','mutedPlaybackVerified','closeControlVerified','requiresExplicitOptIn']) {
    assert.equal(isVideoConfigReady({...approved,[key]:false},'jobpath-india.pages.dev'),false,key);
  }
});
test('only production host and exact approved HTTPS embed host',()=>{
  for(const host of ['example.com','preview.jobpath-india.pages.dev','localhost'])
    assert.equal(isVideoConfigReady(approved,host),false);
  for(const url of ['http://approved-video.example/embed/123','https://evil.example/embed/123',
    'https://approved-video.example.evil.test/embed/123','javascript:alert(1)'])
    assert.equal(isVideoConfigReady({...approved,embedUrl:url},'jobpath-india.pages.dev'),false,url);
});
test('an explicit opt-in is required; no video on GPC',()=>{
  const win={location:{hostname:'jobpath-india.pages.dev'},navigator:{globalPrivacyControl:false}};
  const doc={querySelector(){throw Error('should not read DOM without consent')}};
  assert.equal(mountProfessionalVideo(approved,null,doc,win),false);
  assert.equal(mountProfessionalVideo(approved,'deny',doc,win),false);
  assert.equal(mountProfessionalVideo(approved,'allow',doc,{...win,navigator:{globalPrivacyControl:true}}),false);
});
test('existing Adsterra configuration is untouched',()=>{
  const ads = JSON.parse(readFileSync('data/ads-config.json','utf8'));
  assert.equal(ads.cloudflareAdsterra.enabled,true);
  assert.equal(ads.cloudflareBanners.enabled,true);
});
