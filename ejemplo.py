import streamlit as st

def main():
    tailwind_code = """
    <link href="https://unpkg.com/tailwindcss@2.2.4/dist/tailwind.min.css" rel="stylesheet">

    <h1 class="text-3xl font-bold underline">
        Indicadores Jis Parking
    </h1>

    <!-- component -->
    <div class="max-w-full mx-4 py-6 sm:mx-auto sm:px-6 lg:px-8">
        <div class="sm:flex sm:space-x-4">
            <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow transform transition-all mb-4 w-full sm:w-1/3 sm:my-8">
                <div class="bg-white p-5">
                    <div class="sm:flex sm:items-start">
                        <div class="text-center sm:mt-0 sm:ml-2 sm:text-left">
                            <h3 class="text-sm leading-6 font-medium text-gray-400">Total Subscribers</h3>
                            <p class="text-3xl font-bold text-black">71,897</p>
                        </div>
                    </div>
                </div>
            </div>
            <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow transform transition-all mb-4 w-full sm:w-1/3 sm:my-8">
                <div class="bg-white p-5">
                    <div class="sm:flex sm:items-start">
                        <div class="text-center sm:mt-0 sm:ml-2 sm:text-left">
                            <h3 class="text-sm leading-6 font-medium text-gray-400">Avg. Open Rate</h3>
                            <p class="text-3xl font-bold text-black">58.16%</p>
                        </div>
                    </div>
                </div>
            </div>
            <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow transform transition-all mb-4 w-full sm:w-1/3 sm:my-8">
                <div class="bg-white p-5">
                    <div class="sm:flex sm:items-start">
                        <div class="text-center sm:mt-0 sm:ml-2 sm:text-left">
                            <h3 class="text-sm leading-6 font-medium text-gray-400">Avg. Click Rate</h3>
                            <p class="text-3xl font-bold text-black">24.57%</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """
    # Renderizar el código HTML junto con los estilos de Tailwind CSS
    st.markdown(tailwind_code, unsafe_allow_html=True)

if __name__ == "__main__":
    main()



