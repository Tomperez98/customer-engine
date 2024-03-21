'use client'
import {useState} from 'react'
import {FormTemplate} from '@/types/Forms'
import {BASE_URL} from '@/constants/url'
import {useKindeBrowserClient} from '@kinde-oss/kinde-auth-nextjs'

const useCreateForm = (data: FormTemplate) => {
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState(null)
    const {accessTokenEncoded} = useKindeBrowserClient()

    const submit = async () => {
        const headers = {
            'Authorization': `Bearer ${accessTokenEncoded}`,
            'Content-Type': 'application/json',
        }
        setIsLoading(true)
        setError(null)
        try {
            const response = await fetch(`${BASE_URL}/automatic-responses`, {
                method: 'POST',
                headers: headers,
                body: JSON.stringify(data),
            })
            setIsLoading(false)
            return await response.json()
        } catch (error: any) {
            setError(error)
            setIsLoading(false)
            throw error
        }
    }

    return {submit, isLoading, error}
}

export default useCreateForm
