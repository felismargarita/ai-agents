import './App.css'
import Panel from './panel/Panel';
import { useEffect, useRef, useState } from 'react';
import { Input, Modal } from 'antd';
import request from './utils/request'

function App() {
  const [openModify, setOpenModify] = useState(false)
  const [processing, setProcessing] = useState(false)
  const [prompt, setPrompt] = useState('')
  const elementsRef = useRef<{ targetElement: string, textContent: string }>(null)
  const iframeRef = useRef<HTMLIFrameElement>(null)

  const handleSuccess = () => {
    if (iframeRef.current) {
      // eslint-disable-next-line no-self-assign
      iframeRef.current.src = iframeRef.current?.src
    }
  }



  useEffect(() => {
    window.addEventListener('message', (event) => {
      if (event.origin !== "http://localhost:8000") return;
      console.log(event.data)
      elementsRef.current = event.data
      setOpenModify(true)
    });
  }, [])

  const submit = () => {
    setProcessing(true)
    request({
      url: '/modify-web',
      method: 'put',
      data: {
        ...elementsRef.current,
        prompt,
      }
    }).then(() => {
      handleSuccess()
      setProcessing(false)
      setOpenModify(false)
    })
  }
  return (
    <>
      <iframe ref={iframeRef} className='develop-web-container' src='http://localhost:8000/develop-web'></iframe>
      <Panel onSuccess={() => handleSuccess()} />
      <Modal
        mask={false}
        open={openModify}
        title="修改网页"
        okText="确认修改"
        cancelText="取消"
        onOk={submit}
        cancelButtonProps={{ disabled: processing }}
        okButtonProps={{ loading: processing }}
        onCancel={() => setOpenModify(false)}
        >
        <Input.TextArea value={prompt} onInput={e => setPrompt(e.currentTarget.value)} />
      </Modal>
    </>
  )
}

export default App
