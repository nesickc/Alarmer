package io.github.nesickc.alarmer.shared

import kotlin.test.Test
import kotlin.test.assertEquals

class WireFormatTest {
    @Test
    fun versionMatchesThePipeline() {
        assertEquals(1, WireFormat.VERSION)
    }
}
