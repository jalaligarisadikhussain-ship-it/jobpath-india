import test from 'node:test';
import assert from 'node:assert/strict';
import {WAIT_MS, secureDestination, secondsLeft, plainClick, installApplyGateway} from '../assets/js/job-gateway.mjs';
test('five seconds must fully elapse before unlocking',()=>{
  assert.equal(WAIT_MS,5000);
  assert.equal(secondsLeft(100,100),5);
  assert.equal(secondsLeft(100,1099),5);
  assert.equal(secondsLeft(100,1100),4);
  assert.equal(secondsLeft(100,5099),1);
  assert.equal(secondsLeft(100,5100),0);
});
test('redirect guard rejects non-HTTPS and credentialed URLs',()=>{
  assert.equal(secureDestination('https://ssc.gov.in/'), 'https://ssc.gov.in/');
  for(const url of ['http://ssc.gov.in','javascript:alert(1)','https://a:b@ssc.gov.in','//ssc.gov.in'])
    assert.equal(secureDestination(url),null);
});
test('modified and non-primary clicks are not intercepted',()=>{
  const ev={button:0,defaultPrevented:false,altKey:false,ctrlKey:false,metaKey:false,shiftKey:false};
  assert.equal(plainClick(ev),true);
  for(const change of [{button:1},{defaultPrevented:true},{altKey:true},{ctrlKey:true},{metaKey:true},{shiftKey:true}])
    assert.equal(plainClick({...ev,...change}),false);
});
test('disabled install can be safely imported outside the browser',()=>{
  assert.equal(typeof installApplyGateway({enabled:false}), 'function');
});
