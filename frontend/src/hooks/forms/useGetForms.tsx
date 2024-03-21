import {useEffect, useState} from 'react'
import {Form} from '@/types/Forms'
import {BASE_URL} from '@/constants/url'
import {useKindeBrowserClient} from '@kinde-oss/kinde-auth-nextjs'

type FormListResponse = {
    automatic_response: Form[]
}

export type FormResponse = {
    automatic_response: Form
}

const useGetForms = (id?: string) => {
    const [data, setData] = useState<FormListResponse | FormResponse>()
    const [isLoading, setIsLoading] = useState<boolean>(false)
    const {accessTokenEncoded} = useKindeBrowserClient()

    const url = id
        ? `${BASE_URL}/automatic-responses/${id}`
        : `${BASE_URL}/automatic-responses`

    const fetchForms = async () => {
        if (!accessTokenEncoded) return
        const headers = {
            Authorization: `Bearer ${accessTokenEncoded}`,
        }
        setIsLoading(true)

        try {
            const res = await fetch(url, {
                headers: headers,
            })
            const resJson = await res.json()

            if (id) {
                setData(resJson as FormResponse)
            } else {
                setData(resJson as FormListResponse)
            }
        } catch (error) {
            console.log(error)
        } finally {
            setIsLoading(false)
        }
    }

    useEffect(() => {
        if (accessTokenEncoded) {
            fetchForms()
        }
    }, [accessTokenEncoded])

    const refetch = () => {
        fetchForms()
    }

    return {data, isLoading, refetch}
}

export default useGetForms
