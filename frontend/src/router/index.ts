import { createRouter, createWebHistory } from 'vue-router'
import TablesManager from '@/components/TablesManager.vue'
import FormsManager from '@/components/FormsManager.vue'
import BlockList from '@/components/BlockList.vue'

const router = createRouter({
	history: createWebHistory(import.meta.env.BASE_URL),
	routes: [
		{
			path: '/',
			component: BlockList,
		},
		//{
		//	path: '/create-form',
		//	name: 'create-form',
		//	component: CreateForm,
		//},
		{
			path: '/create-form',
			name: 'create-form',
			component: FormsManager,
		},
		{
			path: '/tables',
			name: 'tables',
			component: TablesManager,
		},
	],
})

export default router
