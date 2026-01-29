import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import { createPinia } from 'pinia';
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';
import './styles/theme.css';
import zhCn from 'element-plus/dist/locale/zh-cn.mjs';
import dayjs from 'dayjs';
import 'dayjs/locale/zh-cn';

const app = createApp(App);
app.use(createPinia());
app.use(router);
dayjs.locale('zh-cn');
app.use(ElementPlus, { locale: zhCn });
app.mount('#app');
