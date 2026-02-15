<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <el-icon :size="48" color="#409EFF"><OfficeBuilding /></el-icon>
        <h1>煤矿技改预算管控系统</h1>
        <p>平煤神马塔能伊斯法拉公司</p>
      </div>
      <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleLogin" class="login-form">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" :prefix-icon="User" size="large" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" placeholder="密码" type="password" :prefix-icon="Lock" size="large" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit" :loading="loading" size="large" class="login-btn">
            登 录
          </el-button>
        </el-form-item>
      </el-form>
      <div class="demo-accounts">
        <el-divider>演示账号</el-divider>
        <div class="account-list">
          <el-tag @click="fillAccount('admin', 'admin123')" class="account-tag" effect="plain">管理员: admin / admin123</el-tag>
          <el-tag @click="fillAccount('leader', 'leader123')" class="account-tag" type="success" effect="plain">领导: leader / leader123</el-tag>
          <el-tag @click="fillAccount('engineer', 'eng123')" class="account-tag" type="warning" effect="plain">工程部: engineer / eng123</el-tag>
          <el-tag @click="fillAccount('viewer', 'view123')" class="account-tag" type="info" effect="plain">普通: viewer / view123</el-tag>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const formRef = ref()
const loading = ref(false)
const form = reactive({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

function fillAccount(u: string, p: string) {
  form.username = u
  form.password = p
}

async function handleLogin() {
  try {
    await formRef.value?.validate()
  } catch { return }
  loading.value = true
  try {
    await authStore.login(form.username, form.password)
    ElMessage.success('登录成功')
    router.push('/dashboard')
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
}
.login-card {
  width: 420px;
  background: #fff;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}
.login-header {
  text-align: center;
  margin-bottom: 32px;
}
.login-header h1 {
  font-size: 22px;
  color: #303133;
  margin: 12px 0 4px;
}
.login-header p {
  color: #909399;
  font-size: 14px;
}
.login-btn {
  width: 100%;
}
.demo-accounts {
  margin-top: 8px;
}
.account-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}
.account-tag {
  cursor: pointer;
  font-size: 12px;
}
.account-tag:hover {
  opacity: 0.8;
}
</style>
