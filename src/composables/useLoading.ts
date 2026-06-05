import { ref } from 'vue'

export function useLoading() {
  const isLoading = ref(false)

  async function withLoading<T>(task: () => Promise<T>): Promise<T> {
    isLoading.value = true
    try {
      return await task()
    } finally {
      isLoading.value = false
    }
  }

  return { isLoading, withLoading }
}
