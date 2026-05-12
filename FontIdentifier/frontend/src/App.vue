<template>
  <div class="app-container">
    <header class="header">
      <div class="header-content">
        <h1 class="logo">书法字体识别器</h1>
        <nav class="nav">
          <router-link to="/" class="nav-link">
            <span class="nav-icon">🔍</span>
            字体识别
          </router-link>
          <router-link to="/library" class="nav-link">
            <span class="nav-icon">📚</span>
            字体库
          </router-link>
          <router-link to="/history" class="nav-link">
            <span class="nav-icon">📋</span>
            历史记录
          </router-link>
        </nav>
      </div>
    </header>
    <main class="main-content">
      <router-view />
    </main>
    <footer class="footer">
      <p>书法字体识别器 v1.0.0 | 面向书法研究者和爱好者的专业工具</p>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>
