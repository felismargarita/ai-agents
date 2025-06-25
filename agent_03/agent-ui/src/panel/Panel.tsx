import { Button, Modal, Tooltip, Input, message, Form, Radio, ColorPicker } from 'antd';
import { SettingOutlined } from '@ant-design/icons';
import type React from 'react';
import { useState } from 'react';
import request from '../utils/request'
import './style.css';

const { TextArea } = Input

interface PanelProps {
  onSuccess: () => void
}

const Panel: React.FC<PanelProps> = ({ onSuccess }) => {
  const [open, setOpen] = useState(true)
  const [form] = Form.useForm()
  const [processing, setProcessing] = useState(false)

  const generateWeb = async () => {
    const data = await form.validateFields()
    message.info('页面生成中,请稍等片刻~~~~~~~~')
    setProcessing(true)
    return request({
      url: '/generate-web',
      method: 'post',
      data
    }).then(() => {
      onSuccess()
      setProcessing(false)
      setOpen(false)
      message.success('页面生成成功!')
    })
  }
  return (
    <>
    <Tooltip title="开发面板">
      <Button
        size="large"
        type="primary"
        className='panel-btn'
        icon={<SettingOutlined />}
        onClick={() => setOpen(true)}
      />
    </Tooltip>
    <Modal
      title="静态页面开发面板"
      closable
      mask={false}
      open={open}
      okText="生成页面"
      cancelText="取消"
      onCancel={() => setOpen(false)}
      onOk={generateWeb}
      cancelButtonProps={{ disabled: processing }}
      okButtonProps={{ loading: processing }}
      width={800}
    >
      <Form form={form} labelCol={{ span: 4 }}>
        <Form.Item name="design" label="设计风格" rules={[{ required: true }]} initialValue="Minimalist">
          <Radio.Group
            options={[
              { value: 'Minimalist', label: 'Minimalist' },
              { value: 'Google Material Design', label: 'Google Material Design' },
              { value: 'Flat Design', label: 'Flat Design' },
            ]}
          />
        </Form.Item>
        <Form.Item name="theme" label="主题" initialValue="黑暗" rules={[{ required: true }]} >
          <Radio.Group
            options={[
              { value: '黑暗', label: '黑暗' },
              { value: '明亮', label: '明亮' },
            ]}
          />
        </Form.Item>
        <Form.Item name="color" label="主题色" initialValue="#000000" rules={[{ required: true }]} normalize={v => '#' + v.toHex()}>
          <ColorPicker onChange={e => e.toHex()}/>
        </Form.Item>
        <Form.Item name="complex" label="复杂度" initialValue="简单" rules={[{ required: true }]} >
          <Radio.Group
            options={[
              { value: '复杂', label: '复杂' },
              { value: '简单', label: '简单' },
            ]}
            />
        </Form.Item>
        <Form.Item name="industry" label="行业" initialValue="Ai Agent" rules={[{ required: true }]} >
          <Input />
        </Form.Item>
        <Form.Item name="prompt" label="个性化提示词" >
          <TextArea
            placeholder="请输入您的页面提示词"
            rows={8}
          />
        </Form.Item>

      </Form>

      
    </Modal>
    </>
  )
}

export default Panel